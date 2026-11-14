import os

def test_frontend_files():
    files = ['index.html', 'Bara — MODIS & VIIRS 3D Fire Observatory.html']
    required_ids = [
        'globeCanvas', 'embers', 'regionSelect',
        'btnModeHarmonized', 'btnModeRaw', 'btnPipelineModal', 'btnExportCsv',
        'toastBanner', 'toastMessage', 'btnCloseToast',
        'aoiCoordsLabel', 'btnView3D', 'btnView2D', 'map2dWrapper',
        'mapSubtitle', 'btnBasemapDark', 'btnBasemapSat', 'fireMap',
        'chkHarmonized', 'chkModis', 'chkViirs',
        'kpiPeriodBadge', 'kpiHarmonized', 'kpiAnomaly', 'kpiMedianSub',
        'kpiRawTotal', 'kpiRawSplit', 'kpiFrp',
        'btnRampThermal', 'btnRampViridis', 'calendarContainer', 'legendBar',
        'calendarSelectedInfo', 'chartSubtitle', 'comparisonChart',
        'confidenceFilter', 'hotspotTableBody', 'pipelineModal', 'btnCloseModal'
    ]

    for fname in files:
        assert os.path.exists(fname), f"{fname} does not exist"
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()

        missing = [elem_id for elem_id in required_ids if f'id="{elem_id}"' not in content]
        assert not missing, f"Missing IDs in {fname}: {missing}"

        # Check endpoints and API integrations
        assert 'window.API_BASE' in content, f"window.API_BASE missing in {fname}"
        assert '/api/calendar' in content, f"/api/calendar missing in {fname}"
        assert '/api/hotspots' in content, f"/api/hotspots missing in {fname}"
        assert '/api/export' in content, f"/api/export missing in {fname}"
        assert 'update3DHotspots' in content, f"update3DHotspots missing in {fname}"
        assert 'renderCalendar' in content, f"renderCalendar missing in {fname}"
        assert 'renderChart' in content, f"renderChart missing in {fname}"
        assert 'renderTable' in content, f"renderTable missing in {fname}"

        # Check typography, palettes & UI polish items
        assert 'Bricolage Grotesque' in content, f"Bricolage Grotesque missing in {fname}"
        assert 'DM Sans' in content, f"DM Sans missing in {fname}"
        assert 'Space Mono' in content, f"Space Mono missing in {fname}"
        assert '--ember: #FF5A1F' in content, f"Ember palette missing in {fname}"
        assert 'cal-val' in content, f"Calendar heatmap number de-noising missing in {fname}"

    # Verify both files are strictly identical
    with open(files[0], 'r', encoding='utf-8') as f1, open(files[1], 'r', encoding='utf-8') as f2:
        c1 = f1.read()
        c2 = f2.read()
        assert c1 == c2, f"index.html ({len(c1)} bytes) and Bara file ({len(c2)} bytes) are not identical!"

    print(f"All frontend verification assertions passed successfully across {len(files)} files ({len(c1)} bytes each)!")

if __name__ == '__main__':
    test_frontend_files()
