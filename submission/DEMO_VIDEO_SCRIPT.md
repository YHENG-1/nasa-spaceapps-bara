# Bara — 2-Minute 30-Second Demo Video Script
## NASA Space Apps Challenge 2026 — Johor Bahru Local Event
**Challenge:** Harmonization of MODIS and VIIRS Hot Spots  
**Project:** Bara — Multi-Decadal 3D Peatland & Wildfire Observatory  
**Target Runtime:** 02:30 (150 Seconds)  
**Format:** Dual-Track Script (Visual Cues + Timed Narrator Spoken Audio + On-Screen Text)  

---

## ⏱️ Video Structure Overview

| Scene | Timestamp | Duration | Focus Area |
| :--- | :--- | :--- | :--- |
| **Scene 1** | 00:00 – 00:20 | 20 sec | The Sensor Mismatch Crisis & Project Intro |
| **Scene 2** | 00:20 – 00:50 | 30 sec | Harmonization Engine: DBSCAN & FRP Weighting |
| **Scene 3** | 00:50 – 01:25 | 35 sec | 3D Planetary Globe & Synchronized 2D AOI Inspector |
| **Scene 4** | 01:25 – 01:55 | 30 sec | 2003–2026 Burning Calendar & Anomaly Detection |
| **Scene 5** | 01:55 – 02:15 | 20 sec | Custom AOI Bounding Box Tool & Operational CSV Export |
| **Scene 6** | 02:15 – 02:30 | 15 sec | Impact on Bomba Malaysia, Carbon Preservation & Conclusion |

---

## 🎬 Detailed Shot-by-Shot Script

### **Scene 1: The Sensor Mismatch Crisis (00:00 – 00:20)**

- **Visual Cues:**
  - `[00:00 - 00:05]` Dynamic intro title card: NASA Space Apps Johor Bahru badge, glowing "BARA" logo with smoldering embers animation.
  - `[00:05 - 00:12]` Split-screen footage: Left shows satellite pass of MODIS (coarse 1 km resolution grids); Right shows VIIRS (high-density 375 m resolution dots) over the same fire patch in Johor.
  - `[00:12 - 00:20]` Close-up: Red warning icon showing how 1 fire generates 1 point in MODIS but 8 overlapping points in VIIRS, skewing media statistics.
- **On-Screen Text (OST):**
  - *"Bara: Harmonizing MODIS & VIIRS Hotspots"*
  - *"The Problem: 1 km vs 375 m Sensor Mismatch"*
  - *"False Fire Count Inflation: +700% Duplicate Hotspots"*
- **Narrator (Spoken Audio):**
  > *(Urgent, authoritative tone)*  
  > *"Every dry season across Southeast Asia, smoldering peatlands threaten our climate and air quality. But our frontline firefighters face a critical data paradox: NASA’s MODIS observes fires at 1 kilometer, while VIIRS sees them at 375 meters. The result? Artificial hotspot count inflation, duplicate alerts, and fragmented operational intelligence. Welcome to **Bara**—the unified multi-sensor fire observatory."*

---

### **Scene 2: The Harmonization Engine (00:20 – 00:50)**

- **Visual Cues:**
  - `[00:20 - 00:30]` Animated architectural diagram showing raw NASA FIRMS API streaming into Python FastAPI backend.
  - `[00:30 - 00:40]` Graphic animation of **Spatio-Temporal Haversine DBSCAN**: circles grouping MODIS (1km) and VIIRS (375m) points within a 1.0 km radius and 24-hour temporal window into a single cluster.
  - `[00:40 - 00:50]` Mathematical formula highlight: Centroid recalculation weighted by **Fire Radiative Power (FRP)**, collapsing the cluster into an exact physical hotspot center.
- **On-Screen Text (OST):**
  - *"Spatio-Temporal Haversine DBSCAN (1 km / 24h Window)"*
  - *"FRP-Weighted Centroid & Energy Conservation"*
  - *"Eliminates Duplicate Detections | Preserves Total Radiative Power"*
- **Narrator (Spoken Audio):**
  > *(Analytical, confident tone)*  
  > *"At the core of Bara is an automated Spatio-Temporal Harmonization Engine. Using spherical Haversine DBSCAN clustering across a 24-hour window, Bara merges overlapping multi-satellite detections into single, unified fire events. We don’t just average coordinates—we calculate an FRP-weighted centroid, pulling the hotspot marker directly into the highest-energy flaming core while preserving 100% of the true Fire Radiative Power."*

---

### **Scene 3: Live 3D Globe & 2D AOI Inspector (00:50 – 01:25)**

- **Visual Cues:**
  - `[00:50 - 01:00]` Screen capture of Bara web application: Interactive Three.js 3D Earth globe rotating smoothly, glowing vertical flame pillars indicating regional fire concentrations.
  - `[01:00 - 01:08]` User clicks the preset button: **"Johor & Southern Malaysia"**. Camera smoothly zooms into Johor, synchronized 2D Leaflet map below snaps to the exact bounding box.
  - `[01:08 - 01:25]` User toggles the **"Harmonized vs. Raw Sensors"** switch.
    - *Raw Mode:* The screen shows hundreds of scattered, overlapping blue (VIIRS) and orange (MODIS) dots.
    - *Harmonized Mode:* Clustered glow rings emerge with clear cluster sizes and single consolidated pins. User clicks a cluster popup showing: *"Cluster #142 | MODIS: 2 | VIIRS: 9 | Combined FRP: 184.2 MW | Conf: High"*.
- **On-Screen Text (OST):**
  - *"Dual-Engine: Three.js 3D WebGL + Leaflet 2D Cartography"*
  - *"Harmonized vs. Raw Sensor Toggle: Instant Clarity"*
  - *"Popup Metric: Unified FRP, Breakdown Counts, Spatial Footprint"*
- **Narrator (Spoken Audio):**
  > *(Enthusiastic, demonstrative tone)*  
  > *"Here is Bara in action. On our 3D Three.js globe, fire energy rises dynamically as volumetric flame pillars. Clicking our home region of Johor smoothly repositions both our 3D view and our high-resolution 2D Leaflet map. Watch what happens when we toggle between Raw and Harmonized modes: a chaotic swarm of over a dozen raw satellite points instantly condenses into one clear, actionable perimeter, complete with sensor breakdown and combined radiative output."*

---

### **Scene 4: Burning Activity Calendar & Anomaly Engine (01:25 – 01:55)**

- **Visual Cues:**
  - `[01:25 - 01:35]` Cursor scrolls down to the **Burning Activity Calendar**. 12-month by 12-year grid (2015–2026) displayed in vibrant Thermal Heatmap colors.
  - `[01:35 - 01:42]` User clicks the **"Palette: Viridis"** button. The calendar smoothly transitions to a colorblind-safe accessible Viridis spectrum.
  - `[01:42 - 01:55]` User clicks **September 2023** cell (severe El Niño season).
    - Map instantly filters to show September 2023 hotspots.
    - Chart.js seasonal curve updates, showing an orange spike towering over the 2003–2025 climatological median line (+145% Anomaly badge flashes).
- **On-Screen Text (OST):**
  - *"Multi-Decadal Burning Matrix (2003–2026 Baseline)"*
  - *"Accessible Colorblind Palettes: Thermal & Viridis"*
  - *"Climatological Anomaly vs. 23-Year Median"*
- **Narrator (Spoken Audio):**
  > *(Engaging, exploratory tone)*  
  > *"To place today’s fires in historical context, Bara introduces the Decadal Burning Activity Calendar. By comparing harmonized monthly events against our 23-year historical baseline (2003 to 2025), Bara automatically flags climatological anomalies. Selecting September during the 2023 El Niño immediately reveals a plus-145 percent surge above baseline, simultaneously updating our temporal charts and spatial observatory."*

---

### **Scene 5: Custom AOI Bounding Box & CSV Export (01:55 – 02:15)**

- **Visual Cues:**
  - `[01:55 - 02:05]` User clicks **"Custom AOI Bounding Box"** button on the map toolbar. A modal appears: user enters coordinates `[West: 102.5, South: 1.2, East: 104.5, North: 2.8]`. Map instantly bounds to the custom polygon, queries FastAPI `/api/hotspots`, and renders harmonized clusters.
  - `[02:05 - 02:15]` User clicks the green **"Export Harmonized CSV"** button. File downloads immediately; brief flash of clean CSV spreadsheet with columns `cluster_id, lat, lng, frp_mw, modis_count, viirs_count, anomaly_pct`.
- **On-Screen Text (OST):**
  - *"Arbitrary Coordinate Querying: Global Custom AOI"*
  - *"FastAPI Streaming CSV Export for Field Operations"*
  - *"Zero-Lockin Open Data Standard"*
- **Narrator (Spoken Audio):**
  > *(Practical, workflow-focused tone)*  
  > *"Bara isn’t limited to preset areas. Disaster coordinators can define custom geographic bounding boxes anywhere on the globe for instant harmonization. And with our one-click CSV export, field teams receive ready-to-ingest datasets compatible with QGIS, ArcGIS, and incident command systems."*

---

### **Scene 6: Real-World Impact & Closing Call to Action (02:15 – 02:30)**

- **Visual Cues:**
  - `[02:15 - 02:22]` Montage: Malaysian BOMBA fire trucks deploying to peatland forest; satellite orbital view of Earth; clean air over Johor Bahru skyline.
  - `[02:22 - 02:30]` Outro card: Team Bara, GitHub repository link, Docker 1-click badge, NASA Space Apps Johor Bahru 2026 logo.
- **On-Screen Text (OST):**
  - *"Bara: Protecting Communities, Peatlands & Climate"*
  - *"Open Source • Docker Ready • 100% NASA FIRMS Powered"*
  - *"NASA Space Apps Challenge 2026 — Johor Bahru Local Event"*
- **Narrator (Spoken Audio):**
  > *(Inspirational, memorable closing)*  
  > *"From space to soil, Bara bridges satellite generations to give Earth’s fire protectors a single, truthful picture. Deployed via Docker with zero cloud lock-in, Bara is ready to safeguard our peatlands, our communities, and our planet. Thank you!"*

---

## 🎙️ Recording & Production Checklist

- [x] **Duration Check:** 150 seconds (2:30) spoken at a steady 130–140 words per minute (~340 words total).
- [x] **Voice Tone:** Professional, articulate, clear pacing, broadcast quality.
- [x] **Screen Capture Settings:** 1080p 60fps, cursor highlight enabled, browser zoom set to 100%.
- [x] **Audio Mixing:** Background ambient electronic synthesizer at -22 dB; narrator voiceover normalized to -3 dB.
- [x] **Subtitles:** Embedded English SRT file provided for accessibility and international judging compliance.
