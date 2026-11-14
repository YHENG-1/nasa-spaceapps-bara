# NASA Space Apps Challenge 2026 — Official Project Submission Form
## Johor Bahru Local Event

---

### 1. Basic Information
- **Project Title:** Bara — Spatio-Temporal Harmonization of MODIS & VIIRS Hot Spots
- **Challenge:** Harmonization of MODIS and VIIRS Hot Spots
- **Local Event:** Johor Bahru, Malaysia
- **Team Name:** Team Bara
- **Project URL:** https://github.com/team-bara/bara-fire-observatory
- **Demo / Deployment URL:** http://localhost:8000
- **Pitch Deck:** `submission/PITCH_DECK.md`
- **Demo Video Script:** `submission/DEMO_VIDEO_SCRIPT.md`

---

### 2. High-Level Project Summary (Short Description)
*Peatland wildfires in Southeast Asia smolder beneath the soil for months, releasing gigatons of carbon into the atmosphere. However, fire responders face a satellite data dilemma: NASA's MODIS instrument detects fires at a 1 km resolution, while VIIRS observes at 375 m. This spatial mismatch causes artificial "hotspot count inflation" (up to 7–9 VIIRS detections per 1 MODIS detection), confusing emergency teams and media reports.*

*Bara ("Ember" in Malay) is a full-stack spatio-temporal harmonization engine and interactive 3D/2D wildfire observatory. Built on spherical Haversine DBSCAN clustering (1 km radius / 24-hour window) and Fire Radiative Power (FRP) centroid weighting, Bara collapses duplicate sensor detections into unified, energy-conserved Fire Events. By benchmarking harmonized events against a 23-year historical baseline (2003–2025), Bara automatically detects extreme seasonal burning anomalies, equipping agencies like BOMBA Malaysia and ASEAN disaster centers with a single, clear truth from space.*

---

### 3. Detailed Project Description

#### What Does It Do?
Bara provides an end-to-end pipeline connecting NASA FIRMS satellite data streams directly to an operational wildfire command dashboard:
1. **Spatio-Temporal Harmonization:** Unifies overlapping MODIS (1km) and VIIRS (375m) hotspot detections into consolidated fire events using spherical DBSCAN with haversine distance.
2. **Energy Conservation & Accurate Centroiding:** Rather than simple geometric averaging, Bara calculates cluster centers weighted by Fire Radiative Power (FRP), anchoring the hotspot marker to the active burning front. Total radiative power is 100% conserved across sensor platforms.
3. **Decadal Climatological Anomaly Tracking:** Computes monthly median baseline values from 2003 to 2025 and calculates percentage anomalies to immediately differentiate routine agricultural burning from catastrophic ecological disasters.
4. **Dual 3D/2D Synchronized Interface:** Features a 3D Three.js WebGL globe with volumetric flame pillars synchronized with an interactive Leaflet 2D map featuring an instant "Harmonized vs. Raw Sensors" toggle and custom bounding-box querying.
5. **Decadal Burning Calendar:** Interactive multi-year matrix (2015–2026) equipped with Thermal and CVD-accessible Viridis color ramps for rapid historical pattern exploration.
6. **Field-Ready Export:** Streams filtered, harmonized fire events directly to CSV for ingestion into QGIS, ArcGIS, or incident command systems.

---

### 4. Space Agency Data & Open Resources Used

1. **NASA FIRMS (Fire Information for Resource Management System) NRT API:**
   - Near real-time active fire / thermal anomaly detections for MODIS C6.1, VIIRS S-NPP (VNP14IMGTDL), and VIIRS NOAA-20 (VJ114IMGTDL).
2. **NASA FIRMS Archive Download:**
   - Multi-decadal historical active fire observations (2003–2025) for Southeast Asia to establish long-term climatological median baselines.
3. **NASA POWER (Prediction Of Worldwide Energy Resources) API:**
   - Climatological surface meteorology, diurnal wind vectors, and relative humidity indices for fire vulnerability context.
4. **Natural Earth / World Atlas GeoJSON:**
   - Topological coastline and national administrative boundary data for 3D sphere projection.

---

### 5. Technical Stack & Architecture

- **Backend:** Python 3.11, FastAPI, Uvicorn, Scikit-learn (Haversine DBSCAN), Pandas, NumPy, HTTPX, Pydantic.
- **Frontend:** Vanilla JavaScript (ES6+), Three.js (WebGL 3D Earth & shader flame pillars), Leaflet.js (2D Cartography & ArcGIS Dark/Satellite tiles), Chart.js (Seasonal baseline comparison), Lucide Icons.
- **DevOps & Cloud:** Docker, Docker Compose, Render (`render.yaml`), Procfile.

---

### 6. Hackathon Journey & Lessons Learned
During development, our primary challenge was ensuring the harmonization algorithm did not discard valuable high-resolution details from VIIRS while solving the double-counting problem. We addressed this by engineering an FRP-weighted centroid calculation and preserving both raw sensor counts within each cluster payload. This provides both simplified operational clarity for incident commanders and granular audit trails for climate researchers.
