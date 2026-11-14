"""
Seed historical MODIS and VIIRS records (2015-2026) for Johor, Kalimantan, and SE Asia.
Ensures instant offline functionality with rich datasets.
"""

import json
import math
import random
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

REGIONS = {
    "johor": {
        "name": "Johor & Southern Malaysia",
        "bbox": [102.4, 1.2, 104.5, 2.8],
        "seasonalCurve": [18, 32, 48, 25, 14, 22, 39, 64, 78, 42, 16, 12],
        "seeds": [
            ("Kota Tinggi Peatland", 1.542, 103.981, 34.2, "High", 1, 3),
            ("Kluang Agro Zone", 1.849, 103.318, 18.7, "Nominal", 1, 2),
            ("Kulai Corridor", 1.663, 103.601, 26.4, "High", 0, 2),
            ("Muar Coastal Scrub", 2.041, 102.569, 41.8, "High", 2, 4),
            ("Pengerang East", 1.491, 104.142, 15.1, "Nominal", 1, 1),
            ("Segamat Forest Edge", 2.285, 103.175, 29.5, "High", 1, 3),
            ("Pontian Peat Buffer", 1.384, 103.521, 22.0, "Nominal", 1, 2),
            ("Batu Pahat Scrub", 1.854, 102.932, 24.1, "Nominal", 1, 2),
            ("Mersing Coastal Ridge", 2.431, 103.840, 31.0, "High", 1, 3),
        ],
    },
    "kalimantan": {
        "name": "Central Kalimantan Peatlands",
        "bbox": [111.0, -3.6, 115.6, -0.6],
        "seasonalCurve": [30, 35, 55, 45, 70, 120, 210, 390, 520, 340, 95, 40],
        "seeds": [
            ("Pulang Pisau Peat Dome", -2.312, 114.115, 78.4, "High", 3, 7),
            ("Sebangau Buffer", -2.084, 113.782, 62.1, "High", 2, 5),
            ("Kapuas Mega-Rice Zone", -2.541, 114.382, 94.6, "High", 4, 9),
            ("Katingan Ridge", -1.912, 113.524, 33.8, "Nominal", 1, 3),
            ("Mendawai Wetlands", -2.418, 113.611, 51.2, "High", 2, 4),
            ("Barito Basin South", -2.145, 114.265, 45.9, "Nominal", 1, 4),
            ("Sampit Peat Plains", -2.533, 112.950, 68.2, "High", 2, 6),
            ("Palangka Raya Fringe", -2.208, 113.916, 55.0, "High", 2, 5),
        ],
    },
    "sea": {
        "name": "Southeast Asia Regional",
        "bbox": [95.0, -11.0, 141.0, 20.0],
        "seasonalCurve": [180, 310, 540, 420, 260, 350, 580, 920, 1180, 760, 280, 190],
        "seeds": [
            ("Johor, Malaysia", 1.542, 103.981, 34.2, "High", 2, 4),
            ("Central Kalimantan, IDN", -2.312, 114.115, 86.5, "High", 4, 8),
            ("Riau Peatlands, IDN", 0.512, 101.447, 71.0, "High", 3, 6),
            ("Sarawak West, Malaysia", 1.553, 110.359, 29.4, "Nominal", 1, 3),
            ("Jambi Basin, IDN", -1.610, 103.613, 64.3, "High", 2, 5),
            ("North Sumatra, IDN", 3.595, 98.672, 38.7, "Nominal", 1, 3),
            ("South Sumatra Wetlands", -3.200, 104.750, 75.3, "High", 3, 7),
            ("West Kalimantan Coastal", -0.020, 109.340, 52.8, "Nominal", 2, 4),
        ],
    },
}

def generate_region_csv(region_key: str):
    info = REGIONS[region_key]
    seeds = info["seeds"]
    curve = info["seasonalCurve"]

    records = []
    years = range(2015, 2027)

    random.seed(42)  # reproducible

    for yr in years:
        el_nino = (yr in {2015, 2019, 2023, 2026})
        boost = 1.35 if el_nino else 0.85

        for m_idx in range(12):
            month_num = m_idx + 1
            month_str = f"{month_num:02d}"
            base_events = int(max(3, round(curve[m_idx] * boost * (0.8 + 0.4 * random.random()))))

            # Sample seeds for this month
            for _ in range(base_events):
                seed = random.choice(seeds)
                area_name, lat_s, lng_s, frp_s, conf_s, m_cnt, v_cnt = seed

                # Pick a random day in month
                day = random.randint(1, 28)
                date_str = f"{yr}-{month_str}-{day:02d}"

                # Slight jitter per event cluster
                c_lat = lat_s + random.uniform(-0.06, 0.06)
                c_lng = lng_s + random.uniform(-0.06, 0.06)
                cluster_frp = frp_s * (0.75 + 0.5 * random.random())

                # MODIS detections (1km)
                num_modis = max(0, int(round(m_cnt * random.uniform(0.6, 1.4))))
                for i in range(num_modis):
                    records.append({
                        "latitude": round(c_lat + random.uniform(-0.008, 0.008), 5),
                        "longitude": round(c_lng + random.uniform(-0.008, 0.008), 5),
                        "brightness": round(310.0 + cluster_frp * 0.7, 1),
                        "scan": 1.0,
                        "track": 1.0,
                        "acq_date": date_str,
                        "acq_time": f"{1030 + random.randint(0, 120):04d}",
                        "satellite": "Aqua" if random.random() > 0.5 else "Terra",
                        "instrument": "MODIS",
                        "confidence": 85 if conf_s == "High" else 60,
                        "version": "6.1NRT",
                        "bright_t31": 298.0,
                        "frp": round(cluster_frp * (0.85 + 0.3 * random.random()), 1),
                        "daynight": "D",
                        "sensor": "MODIS",
                        "area_name": area_name,
                    })

                # VIIRS detections (375m - higher density)
                num_viirs = max(1, int(round(v_cnt * random.uniform(0.8, 1.5))))
                for i in range(num_viirs):
                    records.append({
                        "latitude": round(c_lat + random.uniform(-0.003, 0.003), 5),
                        "longitude": round(c_lng + random.uniform(-0.003, 0.003), 5),
                        "bright_ti4": round(325.0 + cluster_frp * 0.5, 1),
                        "scan": 0.38,
                        "track": 0.38,
                        "acq_date": date_str,
                        "acq_time": f"{1315 + random.randint(0, 90):04d}",
                        "satellite": "Suomi-NPP" if random.random() > 0.5 else "NOAA-20",
                        "instrument": "VIIRS",
                        "confidence": "h" if conf_s == "High" else "n",
                        "version": "2.0NRT",
                        "bright_ti5": 294.0,
                        "frp": round((cluster_frp / max(1, num_viirs)) * (0.9 + 0.2 * random.random()), 1),
                        "daynight": "D",
                        "sensor": "VIIRS",
                        "area_name": area_name,
                    })

    df = pd.DataFrame(records)
    out_path = DATA_DIR / f"{region_key}_modis_viirs_2015_2026.csv"
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} records for {region_key} -> {out_path}")
    return len(df)

if __name__ == "__main__":
    for r in ["johor", "kalimantan", "sea"]:
        generate_region_csv(r)
