"""
Bara NASA Space Apps Challenge - FastAPI Application & Harmonization Service
Exposes REST endpoints for:
- Spatio-temporal harmonized fire event detections (MODIS + VIIRS)
- Burning Activity Calendar & Historical Baselines (2003-2025)
- NASA FIRMS Live Area API Integration & Seamless Offline Fallback
- CSV Harmonized Export Streaming
"""

import io
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from firms_client import REGION_BOUNDS, FirmsClient
from harmonizer import (
    SpatioTemporalHarmonizer,
    compute_monthly_anomalies,
    compute_monthly_medians,
)

app = FastAPI(
    title="Bara NASA Space Apps API",
    description="Harmonization of MODIS (1km) & VIIRS (375m) Fire Hotspots & Spatio-Temporal Climate Analytics",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
firms_client = FirmsClient()
harmonizer = SpatioTemporalHarmonizer(spatial_eps_km=1.0, min_samples=1)


def parse_bbox_param(bbox_str: Optional[str]) -> Optional[Tuple[float, float, float, float]]:
    """Parse comma-separated 'W,S,E,N' bounding box string."""
    if not bbox_str:
        return None
    try:
        parts = [float(x.strip()) for x in bbox_str.split(",")]
        if len(parts) == 4:
            return (parts[0], parts[1], parts[2], parts[3])
    except Exception:
        pass
    return None


# ==============================================================================
# Models
# ==============================================================================

class HealthResponse(BaseModel):
    status: str = "ok"
    firms_connected: bool
    cached_events: int
    challenge: str = "Harmonization of MODIS and VIIRS Hot Spots"
    timestamp: str


class HarmonizedEvent(BaseModel):
    id: str
    lat: float
    lng: float
    area: str
    modis: int
    modis_count: int
    viirs: int
    viirs_count: int
    frp: float
    conf: str
    date: str
    time: str
    cluster_radius: float
    burn_area_km2: Optional[float] = None


class HotspotsResponse(BaseModel):
    count: int
    region: str
    year: int
    month: int
    events: List[HarmonizedEvent]


class CalendarResponse(BaseModel):
    region: str
    name: str
    matrix: Dict[str, List[int]]
    medians: List[int]
    anomalies: Dict[str, List[int]]
    baseline_range: str


# ==============================================================================
# Endpoints
# ==============================================================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint indicating connection status and pre-cached events."""
    return HealthResponse(
        status="ok",
        firms_connected=firms_client.is_connected(),
        cached_events=firms_client.get_cached_events_count(),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/calendar", response_model=CalendarResponse)
async def get_calendar(
    region: str = Query(default="johor", description="Target region (johor, kalimantan, sea)"),
    bbox: Optional[str] = Query(default=None, description="Optional bounding box 'W,S,E,N'"),
):
    """
    Returns the monthly harmonized fire event matrix (2015-2026),
    the 2003-2025 monthly medians, and anomaly percentages.
    """
    parsed_bbox = parse_bbox_param(bbox)
    data = firms_client.get_calendar_data(region, parsed_bbox)
    return CalendarResponse(**data)


@app.get("/api/hotspots", response_model=HotspotsResponse)
async def get_hotspots(
    region: str = Query(default="johor", description="Region key: johor, kalimantan, sea"),
    year: int = Query(default=2026, description="Year (e.g. 2015-2026)"),
    month: int = Query(default=9, description="Month (1-12 or 0-11)"),
    confidence: str = Query(default="all", description="Filter: all, high, nominal, low"),
    bbox: Optional[str] = Query(default=None, description="Custom bbox 'W,S,E,N'"),
    days: int = Query(default=1, description="Observation days window (1-10)"),
):
    """
    Returns harmonized fire events for a selected year/month,
    merging MODIS (1km) and VIIRS (375m) into unified clusters via DBSCAN.
    """
    # Normalize month (accept 0-11 or 1-12)
    norm_month = month
    if norm_month < 1:
        norm_month = 1
    elif norm_month > 12:
        norm_month = 12

    target_date = f"{year}-{norm_month:02d}-14"

    # Determine bounding box
    parsed_bbox = parse_bbox_param(bbox)
    if not parsed_bbox:
        reg_info = REGION_BOUNDS.get(region.lower(), REGION_BOUNDS["johor"])
        parsed_bbox = tuple(reg_info["bbox"])  # type: ignore

    # Fetch and combine raw MODIS & VIIRS detections
    raw_df = await firms_client.fetch_harmonized_inputs(
        bbox=parsed_bbox,  # type: ignore
        days=days,
        date_str=target_date,
    )

    # Run Spatio-Temporal DBSCAN Harmonization
    clustered_events = harmonizer.cluster_detections(raw_df)

    # Filter by confidence if requested
    conf_filter = confidence.strip().lower()
    if conf_filter != "all":
        clustered_events = [
            ev for ev in clustered_events
            if ev["conf"].lower() == conf_filter
        ]

    # Convert to response objects
    typed_events = [HarmonizedEvent(**ev) for ev in clustered_events]

    return HotspotsResponse(
        count=len(typed_events),
        region=region,
        year=year,
        month=norm_month,
        events=typed_events,
    )


@app.get("/api/export")
async def export_harmonized_csv(
    region: str = Query(default="johor"),
    year: int = Query(default=2026),
    month: int = Query(default=9),
    confidence: str = Query(default="all"),
    bbox: Optional[str] = Query(default=None),
):
    """
    Stream download a clean CSV file of harmonized fire events.
    Matches frontend and scientific analysis format.
    """
    hotspots_data = await get_hotspots(
        region=region,
        year=year,
        month=month,
        confidence=confidence,
        bbox=bbox,
        days=1,
    )

    output = io.StringIO()
    # CSV Header
    output.write("event_id,area,latitude,longitude,modis_count,viirs_count,calibrated_frp_mw,confidence,cluster_radius_km,burn_area_km2,year,month,date,time\n")

    for ev in hotspots_data.events:
        output.write(
            f'{ev.id},"{ev.area}",{ev.lat},{ev.lng},{ev.modis_count},{ev.viirs_count},'
            f'{ev.frp},{ev.conf},{ev.cluster_radius},{ev.burn_area_km2 or 0.25},'
            f'{year},{month},{ev.date},{ev.time}\n'
        )

    output.seek(0)
    filename = f"bara_harmonized_{region}_{year}_M{month:02d}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
