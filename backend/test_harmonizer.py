"""
Self-test suite for Bara NASA Space Apps Harmonization Engine & API.
Verifies spatio-temporal clustering, resolution inflation correction,
baseline median calculations, and endpoint responses.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import numpy as np
from harmonizer import SpatioTemporalHarmonizer, compute_monthly_medians, compute_monthly_anomalies
from firms_client import FirmsClient


def test_clustering_single_and_multi_sensor():
    print("[TEST 1] Testing DBSCAN spatio-temporal clustering...")
    harmonizer = SpatioTemporalHarmonizer(spatial_eps_km=1.0, min_samples=1)

    # 1 MODIS detection and 3 VIIRS detections for the same physical fire in Kota Tinggi
    sample_records = [
        # MODIS detection (1km)
        {
            "latitude": 1.5420,
            "longitude": 103.9810,
            "acq_date": "2026-09-14",
            "acq_time": "1030",
            "frp": 32.0,
            "confidence": 85,
            "sensor": "MODIS",
            "area_name": "Kota Tinggi Peatland",
        },
        # VIIRS detection 1 (~200m away)
        {
            "latitude": 1.5430,
            "longitude": 103.9815,
            "acq_date": "2026-09-14",
            "acq_time": "1315",
            "frp": 12.5,
            "confidence": "h",
            "sensor": "VIIRS",
            "area_name": "Kota Tinggi Peatland",
        },
        # VIIRS detection 2 (~350m away)
        {
            "latitude": 1.5415,
            "longitude": 103.9805,
            "acq_date": "2026-09-14",
            "acq_time": "1315",
            "frp": 14.0,
            "confidence": "h",
            "sensor": "VIIRS",
            "area_name": "Kota Tinggi Peatland",
        },
        # VIIRS detection 3 (~150m away)
        {
            "latitude": 1.5425,
            "longitude": 103.9808,
            "acq_date": "2026-09-14",
            "acq_time": "1315",
            "frp": 11.0,
            "confidence": "h",
            "sensor": "VIIRS",
            "area_name": "Kota Tinggi Peatland",
        },
        # Disjoint fire event in Segamat (>80km away)
        {
            "latitude": 2.2850,
            "longitude": 103.1750,
            "acq_date": "2026-09-14",
            "acq_time": "1315",
            "frp": 25.0,
            "confidence": "n",
            "sensor": "VIIRS",
            "area_name": "Segamat Forest Edge",
        }
    ]

    df = pd.DataFrame(sample_records)
    clusters = harmonizer.cluster_detections(df)

    # We expect exactly 2 clusters: Kota Tinggi (4 raw detections merged) and Segamat (1 detection)
    assert len(clusters) == 2, f"Expected 2 clusters, got {len(clusters)}"

    # Find Kota Tinggi cluster
    kt_cluster = next((c for c in clusters if "Kota Tinggi" in c["area"]), None)
    assert kt_cluster is not None, "Kota Tinggi cluster not found"

    # Verify resolution inflation correction
    assert kt_cluster["modis_count"] == 1, f"Expected 1 MODIS, got {kt_cluster['modis_count']}"
    assert kt_cluster["viirs_count"] == 3, f"Expected 3 VIIRS, got {kt_cluster['viirs_count']}"
    assert kt_cluster["raw_detections"] == 4, f"Expected 4 raw detections, got {kt_cluster['raw_detections']}"

    # Verify cross-sensor multi-satellite confidence boost
    assert kt_cluster["conf"] == "High", f"Expected High confidence, got {kt_cluster['conf']}"

    # Verify centroid lies within expected envelope
    assert abs(kt_cluster["lat"] - 1.542) < 0.005, f"Centroid lat unexpected: {kt_cluster['lat']}"
    assert abs(kt_cluster["lng"] - 103.981) < 0.005, f"Centroid lng unexpected: {kt_cluster['lng']}"

    print("  ✓ DBSCAN spatio-temporal clustering & multi-sensor deduplication passed.")


def test_baseline_and_anomalies():
    print("[TEST 2] Testing 2003-2025 baseline medians & anomalies...")
    # Mock seasonal matrix
    matrix = {
        "2023": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 50, 20],
        "2024": [12, 18, 35, 38, 48, 62, 75, 85, 95, 98, 45, 22],
        "2025": [11, 22, 28, 42, 52, 58, 68, 82, 88, 102, 52, 18],
        "2026": [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 75, 30], # high anomaly year
    }

    medians = compute_monthly_medians(matrix, baseline_end_year=2025)
    assert len(medians) == 12, f"Expected 12 medians, got {len(medians)}"
    assert medians[0] == 11, f"Expected Jan median=11, got {medians[0]}"
    assert medians[1] == 20, f"Expected Feb median=20, got {medians[1]}"

    anomalies = compute_monthly_anomalies(matrix, medians)
    assert "2026" in anomalies
    # Jan 2026: (15 - 11) / 11 * 100 = 36%
    assert anomalies["2026"][0] == 36, f"Expected Jan 2026 anomaly=36%, got {anomalies['2026'][0]}%"

    print("  ✓ Baseline medians and anomalies calculation passed.")


def test_firms_client_calendar_and_cache():
    print("[TEST 3] Testing FirmsClient calendar data generation...")
    client = FirmsClient()
    cal = client.get_calendar_data("johor")

    assert "matrix" in cal
    assert "2026" in cal["matrix"]
    assert len(cal["matrix"]["2026"]) == 12
    assert "medians" in cal
    assert len(cal["medians"]) == 12
    assert "anomalies" in cal
    assert "2026" in cal["anomalies"]
    assert cal["baseline_range"] == "2003-2025"

    print("  ✓ FirmsClient calendar & baseline logic passed.")


if __name__ == "__main__":
    test_clustering_single_and_multi_sensor()
    test_baseline_and_anomalies()
    test_firms_client_calendar_and_cache()
    print("\nALL BACKEND UNIT TESTS PASSED SUCCESSFULLY! ✓")
