import os
import re

def test_frontend_files():
    files = ['index.html', 'Bara — MODIS & VIIRS 3D Fire Observatory.html']
    required_ids = [
        'regionSelect', 'btnOpenAoiModal', 'aoiModal',
        'inputAoiNorth', 'inputAoiWest', 'inputAoiEast', 'inputAoiSouth',
        'btnApplyAoi', 'btnCancelAoi', 'btnCloseAoiModal',
        'btnAoiFromCurrentMap', 'btnMapCaptureAoi',
        'backendStatusBadge', 'backendStatusDot', 'backendStatusLabel',
        'btnExportCsv', 'chkHarmonized', 'chkModis', 'chkViirs',
        'btnModeHarmonized', 'btnModeRaw', 'btnView3D', 'btnView2D',
        'btnBasemapDark', 'btnBasemapSat', 'btnRampThermal', 'btnRampViridis',
        'confidenceFilter', 'kpiHarmonized', 'kpiAnomaly', 'kpiRawTotal',
        'kpiRawSplit', 'kpiFrp', 'calendarContainer', 'comparisonChart',
        'hotspotTableBody', 'aoiCoordsLabel', 'mapSubtitle', 'pipelineModal',
        # UI/UX Pro Max HUD Elements
        'hudActiveClusters', 'hudCumulativeFrp', 'hudBurnArea', 'hudSensorConsensus',
        'btnOpenShortcuts', 'keyboardModal', 'btnCloseKeyboardModal', 'btnKeyboardGotIt',
        'btnHighContrast'
    ]

    for fname in files:
        assert os.path.exists(fname), f"{fname} does not exist"
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()

        missing = [elem_id for elem_id in required_ids if f'id="{elem_id}"' not in content]
        assert not missing, f"Missing IDs in {fname}: {missing}"

        # Check endpoints and fallback
        assert 'window.API_BASE' in content, f"window.API_BASE missing in {fname}"
        assert '/api/calendar' in content, f"/api/calendar missing in {fname}"
        assert '/api/hotspots' in content, f"/api/hotspots missing in {fname}"
        assert '/api/export' in content, f"/api/export missing in {fname}"
        assert '/api/health' in content, f"/api/health missing in {fname}"
        assert 'customBbox' in content, f"customBbox missing in {fname}"
        assert 'updateAoiBoundingBoxDisplay' in content, f"updateAoiBoundingBoxDisplay missing in {fname}"
        assert 'update3DHotspots' in content, f"update3DHotspots missing in {fname}"

        # Check UI/UX Pro Max HUD styling and sensor palettes
        assert 'Exo 2' in content, f"Exo 2 font missing in {fname}"
        assert 'JetBrains Mono' in content, f"JetBrains Mono font missing in {fname}"
        assert '#F59E0B' in content, f"MODIS electric amber palette missing in {fname}"
        assert '#10B981' in content, f"VIIRS neon emerald palette missing in {fname}"
        assert '#EF4444' in content, f"Harmonized plasma flame palette missing in {fname}"
        assert 'pattern-mode' in content, f"Colorblind pattern mode missing in {fname}"

    # Verify both files are strictly identical
    with open(files[0], 'r', encoding='utf-8') as f1, open(files[1], 'r', encoding='utf-8') as f2:
        c1 = f1.read()
        c2 = f2.read()
        assert c1 == c2, f"index.html ({len(c1)} bytes) and Bara file ({len(c2)} bytes) are not identical!"

    print(f"All frontend verification assertions passed successfully across {len(files)} files ({len(c1)} bytes each)!")

if __name__ == '__main__':
    test_frontend_files()
