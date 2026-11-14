"""
Bara NASA Space Apps Challenge - Harmonization Engine
Spatio-Temporal DBSCAN Clustering & Cross-Sensor Harmonization for MODIS and VIIRS Hot Spots.

Addresses:
- VIIRS resolution inflation (375m vs 1km grid)
- Double-counting across multi-satellite orbital overpasses (Terra, Aqua, Suomi-NPP, NOAA-20, NOAA-21)
- Physical FRP cross-calibration & multi-sensor confidence ensembling
- 2003-2025 Historical baseline median & percentage anomaly calculations
"""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

# Earth mean radius in kilometers (WGS84 spherical approximation)
EARTH_RADIUS_KM = 6371.0088

# DBSCAN spatial tolerance: 1.0 km in radians
DBSCAN_EPS_RAD = 1.0 / EARTH_RADIUS_KM  # ~0.000156961 rad


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth in km."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c


def normalize_confidence(conf: Any, sensor: str) -> Tuple[str, float]:
    """
    Standardize MODIS numeric (0-100) or VIIRS categorical ('l','n','h')
    confidence to ('Low'|'Nominal'|'High', score 0.0..1.0).
    """
    if conf is None or (isinstance(conf, float) and math.isnan(conf)):
        return "Nominal", 0.5

    s_str = str(conf).strip().lower()

    if s_str in ["h", "high"]:
        return "High", 0.95
    if s_str in ["n", "nominal", "nom"]:
        return "Nominal", 0.65
    if s_str in ["l", "low"]:
        return "Low", 0.25

    try:
        val = float(conf)
        score = max(0.0, min(100.0, val)) / 100.0
        if val >= 80.0:
            return "High", score
        elif val >= 30.0:
            return "Nominal", score
        else:
            return "Low", score
    except ValueError:
        return "Nominal", 0.5


class SpatioTemporalHarmonizer:
    """
    Harmonizes multi-satellite thermal detections (MODIS 1km + VIIRS 375m)
    using DBSCAN haversine clustering within temporal observation windows.
    """

    def __init__(self, spatial_eps_km: float = 1.0, min_samples: int = 1):
        self.spatial_eps_km = spatial_eps_km
        self.spatial_eps_rad = spatial_eps_km / EARTH_RADIUS_KM
        self.min_samples = min_samples

    def cluster_detections(self, df_detections: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Cluster raw hotspot records into unified fire events.
        Expected columns in df_detections:
        - latitude (float)
        - longitude (float)
        - acq_date (str 'YYYY-MM-DD' or date)
        - acq_time (str or int, e.g. '0630' or 630)
        - frp (float)
        - confidence (str or float)
        - sensor (str 'MODIS' or 'VIIRS')
        - optional: area_name, satellite
        """
        if df_detections.empty:
            return []

        df = df_detections.copy()

        # Standardize dates
        df["acq_date_str"] = df["acq_date"].astype(str)

        # Standardize sensor name
        if "sensor" not in df.columns:
            if "instrument" in df.columns:
                df["sensor"] = df["instrument"].astype(str).str.upper()
            else:
                df["sensor"] = "VIIRS"

        df["sensor"] = df["sensor"].apply(
            lambda s: "MODIS" if "MODIS" in str(s).upper() else "VIIRS"
        )

        if "frp" not in df.columns:
            df["frp"] = 15.0
        df["frp"] = pd.to_numeric(df["frp"], errors="coerce").fillna(10.0)

        clusters: List[Dict[str, Any]] = []
        cluster_global_idx = 1

        # Group by temporal observation window (calendar day <= 24h window)
        for date_str, date_group in df.groupby("acq_date_str"):
            if len(date_group) == 0:
                continue

            # Convert lat/lng to radians for DBSCAN haversine metric
            coords_rad = np.radians(date_group[["latitude", "longitude"]].to_numpy())

            db = DBSCAN(
                eps=self.spatial_eps_rad,
                min_samples=self.min_samples,
                metric="haversine",
            )
            labels = db.fit_predict(coords_rad)

            # Process each cluster
            for cluster_id in np.unique(labels):
                cluster_mask = (labels == cluster_id)
                cluster_members = date_group.iloc[cluster_mask]

                event = self._aggregate_cluster(
                    cluster_members,
                    date_str=date_str,
                    cluster_num=cluster_global_idx,
                )
                clusters.append(event)
                cluster_global_idx += 1

        return clusters

    def _aggregate_cluster(
        self,
        members: pd.DataFrame,
        date_str: str,
        cluster_num: int,
    ) -> Dict[str, Any]:
        """Aggregate constituent detections into a single harmonized fire event."""
        # Weighted centroid: weights proportional to FRP and sensor weight
        # MODIS has 1km pixel, VIIRS 375m; weighting by FRP ensures hotspot core is tracked
        weights = members["frp"].to_numpy().clip(min=1.0)
        total_weight = weights.sum()

        lats = members["latitude"].to_numpy()
        lngs = members["longitude"].to_numpy()

        centroid_lat = float(np.sum(lats * weights) / total_weight)
        centroid_lng = float(np.sum(lngs * weights) / total_weight)

        # Count by sensor
        modis_members = members[members["sensor"] == "MODIS"]
        viirs_members = members[members["sensor"] == "VIIRS"]
        modis_count = int(len(modis_members))
        viirs_count = int(len(viirs_members))

        # Compute cluster envelope radius (km)
        radii_km = [
            haversine_distance_km(centroid_lat, centroid_lng, rlat, rlng)
            for rlat, rlng in zip(lats, lngs)
        ]
        cluster_radius_km = float(max(radii_km)) if radii_km else 0.2
        # Minimum physical resolution radius: ~0.375 km for VIIRS, ~0.5 km for MODIS
        cluster_radius_km = round(max(cluster_radius_km, 0.35 if viirs_count > 0 else 0.5), 2)

        # Cross-calibrated FRP:
        # If both sensors detect the fire in the same window, taking the maximum of sensor-wise
        # aggregated FRP with cross-calibration avoids double-counting overlapping pixel radiative energy.
        modis_frp_sum = float(modis_members["frp"].sum()) if modis_count > 0 else 0.0
        viirs_frp_sum = float(viirs_members["frp"].sum()) if viirs_count > 0 else 0.0

        if modis_count > 0 and viirs_count > 0:
            # Multi-sensor cross-validated cluster:
            # VIIRS 375m I-band and MODIS 1km 4um channel cross-calibration formula
            calibrated_frp = max(modis_frp_sum, viirs_frp_sum * 0.92) * 1.08
        elif modis_count > 0:
            calibrated_frp = modis_frp_sum
        else:
            # For pure VIIRS clusters with multiple 375m pixels overlapping a single flame front,
            # apply de-inflation factor
            calibrated_frp = viirs_frp_sum / (1.0 + 0.15 * max(0, viirs_count - 1))

        calibrated_frp = round(max(2.0, calibrated_frp), 1)

        # Unified Confidence:
        # Cross-satellite detection provides highest confirmation
        conf_scores = []
        for _, row in members.iterrows():
            _, score = normalize_confidence(row.get("confidence"), row["sensor"])
            conf_scores.append(score)

        avg_conf_score = float(np.mean(conf_scores)) if conf_scores else 0.5
        if modis_count >= 1 and viirs_count >= 1:
            # Multi-sensor cross-validation boost!
            unified_conf = "High"
        elif avg_conf_score >= 0.75:
            unified_conf = "High"
        elif avg_conf_score >= 0.35:
            unified_conf = "Nominal"
        else:
            unified_conf = "Low"

        # Representative acquisition time
        acq_time_val = members.iloc[0].get("acq_time", "1200")
        time_str = self._format_time(acq_time_val)

        # Estimated burn area (km2)
        # Using equivalent physical area model
        if cluster_radius_km > 0:
            geometric_area = math.pi * (cluster_radius_km ** 2)
        else:
            geometric_area = 0.25

        pixel_area = (modis_count * 1.0) + (viirs_count * 0.14)
        estimated_area_km2 = round(max(0.14, min(geometric_area, pixel_area * 1.2)), 2)

        # Area name or location descriptor
        area_name = members.iloc[0].get("area_name") or members.iloc[0].get("area")
        if not area_name or pd.isna(area_name):
            area_name = f"Hotspot Cluster ({centroid_lat:.3f}°N, {centroid_lng:.3f}°E)"

        # Unique Event ID: HRM-YYYY-MM-DDD
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            year_str = str(dt.year)
            month_str = f"{dt.month:02d}"
        except Exception:
            year_str = "2026"
            month_str = "09"

        event_id = f"HRM-{year_str}-{month_str}-{cluster_num:03d}"

        return {
            "id": event_id,
            "lat": round(centroid_lat, 4),
            "lng": round(centroid_lng, 4),
            "area": str(area_name),
            "modis": modis_count,
            "modis_count": modis_count,
            "viirs": viirs_count,
            "viirs_count": viirs_count,
            "frp": calibrated_frp,
            "conf": unified_conf,
            "date": date_str,
            "time": time_str,
            "cluster_radius": cluster_radius_km,
            "burn_area_km2": estimated_area_km2,
            "raw_detections": int(len(members)),
        }

    @staticmethod
    def _format_time(time_val: Any) -> str:
        """Convert FIRMS HHMM string or int to 'HH:MM' UTC."""
        t_str = str(time_val).replace(":", "").zfill(4)
        if len(t_str) >= 4:
            return f"{t_str[:2]}:{t_str[2:4]}"
        return "12:00"


# ==============================================================================
# Historical Baseline & Anomaly Engine (2003 - 2025)
# ==============================================================================

def compute_monthly_medians(matrix: Dict[Union[int, str], List[int]], baseline_end_year: int = 2025) -> List[int]:
    """
    Computes 12-month median values across historical baseline years (e.g. 2003-2025).
    """
    medians: List[int] = []
    for m_idx in range(12):
        month_vals = [
            matrix[yr][m_idx]
            for yr in matrix
            if int(yr) <= baseline_end_year and len(matrix[yr]) > m_idx
        ]
        if not month_vals:
            medians.append(10)
            continue
        month_vals.sort()
        mid = len(month_vals) // 2
        if len(month_vals) % 2 != 0:
            median_val = month_vals[mid]
        else:
            median_val = int(round((month_vals[mid - 1] + month_vals[mid]) / 2.0))
        medians.append(max(1, median_val))
    return medians


def compute_monthly_anomalies(
    matrix: Dict[Union[int, str], List[int]],
    medians: List[int],
) -> Dict[str, List[int]]:
    """
    Calculates percentage anomaly vs historical median for each month:
    % Anomaly = round(((val - median) / median) * 100)
    """
    anomalies: Dict[str, List[int]] = {}
    for yr, series in matrix.items():
        anom_list: List[int] = []
        for m_idx, val in enumerate(series):
            med = medians[m_idx] if m_idx < len(medians) and medians[m_idx] > 0 else 1
            pct_diff = round(((val - med) / med) * 100.0)
            anom_list.append(int(pct_diff))
        anomalies[str(yr)] = anom_list
    return anomalies
