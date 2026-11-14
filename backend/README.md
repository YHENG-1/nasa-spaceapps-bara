# Bara — NASA FIRMS MODIS & VIIRS Harmonization Backend

Backend service and spatio-temporal harmonization engine for the **Bara NASA Space Apps Challenge** project (*Harmonization of MODIS and VIIRS Hot Spots*).

## Overview & Scientific Methodology

NASA collects active fire data from two primary satellite sensor suites:
1. **MODIS** (*Terra* & *Aqua* satellites, 1 km spatial resolution at nadir, active since 2000)
2. **VIIRS** (*Suomi-NPP*, *NOAA-20*, *NOAA-21* satellites, 375 m spatial resolution at nadir, active since 2012)

### The Core Problem: Resolution Inflation & Double-Counting
- **Resolution Inflation**: Because VIIRS detects fire at 375m vs MODIS's 1km pixel footprint, a single physical fire front observed by MODIS as 1 pixel often produces 4 to 8 distinct VIIRS detection pixels. Raw detection counts naively suggest fire frequency increased dramatically after 2012, when in reality sensor resolution merely improved.
- **Double-Counting**: When Terra, Aqua, Suomi-NPP, and NOAA satellites pass over an active fire zone on the same day, they detect overlapping thermal signatures.

### The Bara Solution: Spatio-Temporal DBSCAN Harmonization
- **Haversine Distance Metric**: Points are projected to spherical coordinates using $R = 6371.0088\text{ km}$.
- **Neighborhood ($\epsilon$)**: $1.0\text{ km} / R \approx 0.00015696\text{ radians}$, grouping all thermal pixels within the physical 1 km MODIS footprint.
- **Temporal Window**: Detections within the same 24-hour diurnal observation cycle are clustered.
- **Minimum Samples**: `min_samples = 1`, preserving isolated hotspots while grouping multi-pixel fires.
- **Weighted Centroid**: Centroid coordinates are computed weighted by Fire Radiative Power (FRP):
  $$\text{Centroid} = \frac{\sum w_i \cdot \mathbf{x}_i}{\sum w_i}, \quad w_i = \max(1.0, \text{FRP}_i)$$
- **Sensor Breakdown**: Tracks constituent `modis_count` and `viirs_count` per event.
- **Multi-Sensor Validation**: Events confirmed by both MODIS and VIIRS receive automatic "High" confidence.
- **FRP Cross-Calibration**: Prevents double-summing radiative power while compensating for sensor viewing angles.
- **Baseline Anomalies**: Evaluates % deviation against 2003–2025 monthly medians to detect abnormal fire seasons (e.g. El Niño 2015, 2019, 2023, 2026).

---

## API Contract

| Method | Endpoint | Description | Query Parameters |
|---|---|---|---|
| `GET` | `/api/health` | Service status, FIRMS connection, cached records | None |
| `GET` | `/api/calendar` | 2015–2026 Monthly Matrix, 2003–2025 Medians, % Anomalies | `region` (`johor`, `kalimantan`, `sea`), `bbox` (`W,S,E,N`) |
| `GET` | `/api/hotspots` | Spatio-temporally harmonized fire events | `region`, `year`, `month`, `confidence`, `bbox`, `days` |
| `GET` | `/api/export` | CSV download stream of harmonized fire events | `region`, `year`, `month`, `confidence`, `bbox` |

### Sample Response (`GET /api/hotspots?region=johor&year=2026&month=9`)
```json
{
  "count": 7,
  "region": "johor",
  "year": 2026,
  "month": 9,
  "events": [
    {
      "id": "HRM-2026-09-001",
      "lat": 1.542,
      "lng": 103.981,
      "area": "Kota Tinggi Peatland",
      "modis": 1,
      "modis_count": 1,
      "viirs": 3,
      "viirs_count": 3,
      "frp": 34.2,
      "conf": "High",
      "date": "2026-09-14",
      "time": "06:30",
      "cluster_radius": 0.42,
      "burn_area_km2": 0.55
    }
  ]
}
```

---

## Quickstart

```bash
cd backend
pip install -r requirements.txt
python main.py
```
Or run with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
