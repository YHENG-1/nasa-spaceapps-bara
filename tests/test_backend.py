"""
Bara NASA Space Apps Challenge - Comprehensive Test Suite
Verification tests for:
1. DBSCAN Spatio-temporal clustering accuracy (haversine metric, 1km, 24h temporal window)
2. Anomaly calculations vs 2003-2025 baseline medians
3. FastAPI endpoints: /api/health, /api/calendar, /api/hotspots, /api/export
4. CORS headers, fallback resilience, and error handling
"""

import io
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from harmonizer import (
    EARTH_RADIUS_KM,
    SpatioTemporalHarmonizer,
    compute_monthly_anomalies,
    compute_monthly_medians,
    haversine_distance_km,
    normalize_confidence,
)
from firms_client import FirmsClient, REGION_BOUNDS
from main import app


# ==============================================================================
# 1. DBSCAN & Spatio-Temporal Clustering Tests
# ==============================================================================

class TestDBSCANClustering:
    """Verify haversine distance, 1km spatial threshold, and 24h temporal clustering."""

    def test_haversine_distance_accuracy(self):
        """Test great-circle haversine calculation with known geographic points."""
        # Distance from Kota Tinggi (1.542, 103.981) to near point (+0.005 deg lat ~0.556 km)
        lat1, lon1 = 1.5420, 103.9810
        lat2, lon2 = 1.5470, 103.9810
        dist = haversine_distance_km(lat1, lon1, lat2, lon2)
        assert 0.50 <= dist <= 0.60, f"Expected ~0.55 km, got {dist} km"

        # Identical point distance must be 0
        assert haversine_distance_km(lat1, lon1, lat1, lon1) == 0.0

    def test_same_day_within_1km_clusters_together(self):
        """Two hotspots (MODIS + VIIRS) within 1km on same day must merge into 1 cluster."""
        harmonizer = SpatioTemporalHarmonizer(spatial_eps_km=1.0, min_samples=1)
        # 1.5420 to 1.5450 at lon 103.9810 is ~0.33 km apart
        df = pd.DataFrame([
            {
                "latitude": 1.5420,
                "longitude": 103.9810,
                "acq_date": "2026-09-14",
                "acq_time": "0330",
                "frp": 25.0,
                "confidence": 85,
                "sensor": "MODIS",
                "area_name": "Kota Tinggi Core",
            },
            {
                "latitude": 1.5450,
                "longitude": 103.9810,
                "acq_date": "2026-09-14",
                "acq_time": "0645",
                "frp": 18.0,
                "confidence": "h",
                "sensor": "VIIRS",
                "area_name": "Kota Tinggi Core",
            },
        ])

        clusters = harmonizer.cluster_detections(df)
        assert len(clusters) == 1, f"Expected 1 unified cluster, got {len(clusters)}"
        c = clusters[0]
        assert c["modis_count"] == 1
        assert c["viirs_count"] == 1
        assert c["raw_detections"] == 2
        assert c["conf"] == "High"
        assert c["frp"] > 0
        # Centroid should be between 1.5420 and 1.5450
        assert 1.5420 <= c["lat"] <= 1.5450
        assert abs(c["lng"] - 103.9810) < 1e-4

    def test_same_day_beyond_1km_separate_clusters(self):
        """Two hotspots separated by > 1.0 km on the same day must form separate clusters."""
        harmonizer = SpatioTemporalHarmonizer(spatial_eps_km=1.0, min_samples=1)
        # 1.5420 to 1.5700 at lon 103.9810 is ~3.1 km apart
        df = pd.DataFrame([
            {
                "latitude": 1.5420,
                "longitude": 103.9810,
                "acq_date": "2026-09-14",
                "acq_time": "0330",
                "frp": 20.0,
                "confidence": "h",
                "sensor": "VIIRS",
            },
            {
                "latitude": 1.5700,
                "longitude": 103.9810,
                "acq_date": "2026-09-14",
                "acq_time": "0340",
                "frp": 30.0,
                "confidence": 75,
                "sensor": "MODIS",
            },
        ])

        clusters = harmonizer.cluster_detections(df)
        assert len(clusters) == 2, f"Expected 2 separate clusters for distance > 1km, got {len(clusters)}"

    def test_same_location_different_days_separate_clusters(self):
        """Hotspots at identical coordinates but on different dates (>24h) must NOT merge."""
        harmonizer = SpatioTemporalHarmonizer(spatial_eps_km=1.0, min_samples=1)
        df = pd.DataFrame([
            {
                "latitude": 1.5420,
                "longitude": 103.9810,
                "acq_date": "2026-09-14",
                "acq_time": "0400",
                "frp": 25.0,
                "confidence": "h",
                "sensor": "VIIRS",
            },
            {
                "latitude": 1.5420,
                "longitude": 103.9810,
                "acq_date": "2026-09-16",  # 48h later
                "acq_time": "0400",
                "frp": 22.0,
                "confidence": "h",
                "sensor": "VIIRS",
            },
        ])

        clusters = harmonizer.cluster_detections(df)
        assert len(clusters) == 2, "Expected 2 clusters for different dates"
        dates = {c["date"] for c in clusters}
        assert dates == {"2026-09-14", "2026-09-16"}

    def test_multi_sensor_confidence_ensemble(self):
        """Cross-sensor detection (MODIS + VIIRS) yields 'High' confidence ensemble boost."""
        harmonizer = SpatioTemporalHarmonizer(spatial_eps_km=1.0, min_samples=1)
        df = pd.DataFrame([
            {
                "latitude": -2.312,
                "longitude": 114.115,
                "acq_date": "2026-08-10",
                "acq_time": "0515",
                "frp": 45.0,
                "confidence": "n",  # Nominal
                "sensor": "VIIRS",
            },
            {
                "latitude": -2.314,
                "longitude": 114.116,
                "acq_date": "2026-08-10",
                "acq_time": "0530",
                "frp": 50.0,
                "confidence": 60,  # Nominal numeric
                "sensor": "MODIS",
            },
        ])
        clusters = harmonizer.cluster_detections(df)
        assert len(clusters) == 1
        assert clusters[0]["conf"] == "High", "Multi-sensor confirmation must boost to High confidence"

    def test_empty_dataframe_handling(self):
        """Harmonizer handles empty input gracefully without exception."""
        harmonizer = SpatioTemporalHarmonizer()
        clusters = harmonizer.cluster_detections(pd.DataFrame())
        assert clusters == []


# ==============================================================================
# 2. Historical Baseline & Anomaly Engine Tests
# ==============================================================================

class TestHistoricalBaselineAndAnomalies:
    """Verify median calculation across 2003-2025 and % anomaly formulas."""

    def test_compute_monthly_medians_odd_years(self):
        """Median of 3 years [10, 20, 30] should be 20."""
        matrix = {
            "2023": [10] * 12,
            "2024": [20] * 12,
            "2025": [30] * 12,
        }
        medians = compute_monthly_medians(matrix, baseline_end_year=2025)
        assert len(medians) == 12
        assert all(m == 20 for m in medians)

    def test_compute_monthly_medians_even_years(self):
        """Median of 4 years [10, 20, 30, 40] should be round((20+30)/2) = 25."""
        matrix = {
            "2022": [10] * 12,
            "2023": [20] * 12,
            "2024": [30] * 12,
            "2025": [40] * 12,
        }
        medians = compute_monthly_medians(matrix, baseline_end_year=2025)
        assert all(m == 25 for m in medians)

    def test_baseline_excludes_years_beyond_end_year(self):
        """Baseline end year 2025 must exclude 2026 data."""
        matrix = {
            "2024": [10] * 12,
            "2025": [10] * 12,
            "2026": [999] * 12,  # Should NOT affect baseline
        }
        medians = compute_monthly_medians(matrix, baseline_end_year=2025)
        assert all(m == 10 for m in medians)

    def test_compute_monthly_anomalies_percentage(self):
        """Verify percentage formula: round(((val - median) / median) * 100)."""
        matrix = {
            "2025": [20, 50, 100],
            "2026": [30, 25, 100],
        }
        medians = [20, 50, 100]  # val == median -> 0% anomaly
        anomalies = compute_monthly_anomalies(matrix, medians)

        assert "2025" in anomalies
        assert "2026" in anomalies
        # 2025: (20-20)/20 = 0%, (50-50)/50 = 0%, (100-100)/100 = 0%
        assert anomalies["2025"] == [0, 0, 0]
        # 2026: (30-20)/20 = +50%, (25-50)/50 = -50%, (100-100)/100 = 0%
        assert anomalies["2026"] == [50, -50, 0]


# ==============================================================================
# 3. FastAPI Endpoints & Integration Tests
# ==============================================================================

class TestFastAPIEndpoints:
    """Verify all REST API endpoints with TestClient."""

    @pytest.fixture(scope="class")
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_health_endpoint(self, client):
        """GET /api/health returns status ok, firms connection status, and event counts."""
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "firms_connected" in data
        assert isinstance(data["firms_connected"], bool)
        assert "cached_events" in data
        assert data["cached_events"] >= 0
        assert "timestamp" in data

    def test_calendar_endpoint_default(self, client):
        """GET /api/calendar returns regional matrix, 12-month medians, and anomalies."""
        res = client.get("/api/calendar?region=johor")
        assert res.status_code == 200
        data = res.json()
        assert data["region"] == "johor"
        assert "matrix" in data
        assert "medians" in data
        assert len(data["medians"]) == 12
        assert "anomalies" in data
        # Check years 2015-2026 present
        for yr in range(2015, 2027):
            assert str(yr) in data["matrix"], f"Year {yr} missing from calendar matrix"
            assert len(data["matrix"][str(yr)]) == 12
            assert str(yr) in data["anomalies"], f"Year {yr} missing from anomalies"

    def test_calendar_endpoint_regions(self, client):
        """GET /api/calendar works for kalimantan and sea regions."""
        for r in ["kalimantan", "sea"]:
            res = client.get(f"/api/calendar?region={r}")
            assert res.status_code == 200
            data = res.json()
            assert data["region"] == r
            assert len(data["medians"]) == 12

    def test_calendar_custom_bbox(self, client):
        """GET /api/calendar with custom bbox returns valid payload."""
        res = client.get("/api/calendar?region=custom&bbox=103.0,1.2,104.2,2.5")
        assert res.status_code == 200
        data = res.json()
        assert "matrix" in data
        assert len(data["medians"]) == 12

    def test_hotspots_endpoint_default(self, client):
        """GET /api/hotspots returns harmonized clusters with MODIS and VIIRS counts."""
        res = client.get("/api/hotspots?region=johor&year=2026&month=9&confidence=all")
        assert res.status_code == 200
        data = res.json()
        assert "events" in data
        assert "count" in data
        assert data["count"] == len(data["events"])
        assert data["count"] > 0

        # Verify cluster object schema
        event = data["events"][0]
        assert "id" in event
        assert "lat" in event
        assert "lng" in event
        assert "area" in event
        assert "modis_count" in event
        assert "viirs_count" in event
        assert "frp" in event
        assert "conf" in event
        assert "date" in event
        assert "time" in event
        assert "cluster_radius" in event

    def test_hotspots_confidence_filtering(self, client):
        """GET /api/hotspots filters events correctly by confidence."""
        res_high = client.get("/api/hotspots?region=johor&year=2026&month=9&confidence=high")
        assert res_high.status_code == 200
        data_high = res_high.json()
        for ev in data_high["events"]:
            assert ev["conf"].lower() == "high"

    def test_hotspots_month_edge_cases(self, client):
        """Hotspots endpoint handles month clamps (e.g. 0, 13) gracefully."""
        res0 = client.get("/api/hotspots?region=johor&month=0")
        assert res0.status_code == 200
        assert res0.json()["month"] == 1

        res13 = client.get("/api/hotspots?region=johor&month=13")
        assert res13.status_code == 200
        assert res13.json()["month"] == 12

    def test_export_endpoint_csv_stream(self, client):
        """GET /api/export returns text/csv stream with proper headers and data."""
        res = client.get("/api/export?region=johor&year=2026&month=9")
        assert res.status_code == 200
        assert "text/csv" in res.headers.get("content-type", "")
        assert "Content-Disposition" in res.headers
        assert "attachment; filename=" in res.headers["Content-Disposition"]

        content = res.text
        lines = content.strip().split("\n")
        assert len(lines) >= 2, "CSV should contain at least header and one row"
        header = lines[0].split(",")
        assert "event_id" in header
        assert "latitude" in header
        assert "longitude" in header
        assert "modis_count" in header
        assert "viirs_count" in header
        assert "calibrated_frp_mw" in header


# ==============================================================================
# 4. CORS Headers & Error Handling Tests
# ==============================================================================

class TestCORSAndErrorHandling:
    """Verify CORS headers and robustness against malformed inputs."""

    @pytest.fixture(scope="class")
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_cors_headers_present(self, client):
        """API endpoints must return CORS Access-Control-Allow-Origin header."""
        res = client.get("/api/health", headers={"Origin": "http://localhost:3000"})
        assert res.headers.get("access-control-allow-origin") in ["*", "http://localhost:3000"]

        res2 = client.get("/api/calendar?region=johor", headers={"Origin": "http://127.0.0.1:5500"})
        assert res2.headers.get("access-control-allow-origin") in ["*", "http://127.0.0.1:5500"]

    def test_malformed_bbox_handled_safely(self, client):
        """Malformed bbox parameters do not trigger 500 internal server error."""
        res = client.get("/api/hotspots?region=johor&bbox=not,a,valid,bbox")
        assert res.status_code == 200  # Should fall back to default regional bbox

        res_calendar = client.get("/api/calendar?region=johor&bbox=invalid")
        assert res_calendar.status_code == 200
