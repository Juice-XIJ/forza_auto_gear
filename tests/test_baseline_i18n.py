"""Characterization snapshot of the i18n strings exposed by MainWindow.

Pins every StringVar value for each supported language so a future move of
the parallel arrays from ``constants.py`` into JSON resource files cannot
silently change a label.

Run with ``FORZA_UPDATE_SNAPSHOTS=1`` to regenerate.
"""

from __future__ import annotations

import json
import os

import pytest

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "snapshots")


# Names of every StringVar on MainWindow that the i18n code touches.
_I18N_VARS = [
    "select_language_txt", "language_txt", "clutch_shortcut_txt",
    "upshift_shortcut_txt", "downshift_shortcut_txt", "clutch_txt",
    "farm_txt", "offroad_rally_txt", "car_id", "car_perf", "car_drivetrain",
    "tire_information_txt", "accel_txt", "brake_txt", "shift_point_txt",
    "tree_value_txt", "speed_txt", "rpm_txt", "collect_button_txt",
    "analysis_button_txt", "run_button_txt", "pause_button_txt",
    "exit_button_txt", "clear_log_text", "program_info_txt",
]


def _snapshot_for_language(win, lang_index: int) -> dict[str, str]:
    win.text_update(lang_index)
    win.root.update_idletasks()
    return {name: getattr(win, name).get() for name in _I18N_VARS}


@pytest.mark.parametrize("lang_index,suffix", [(0, "en"), (1, "zhcn")])
def test_i18n_snapshot(main_window_factory, lang_index, suffix):
    snapshot_path = os.path.join(SNAPSHOT_DIR, f"i18n_{suffix}.json")
    win = main_window_factory()
    snapshot = _snapshot_for_language(win, lang_index)

    if os.environ.get("FORZA_UPDATE_SNAPSHOTS") == "1" or not os.path.exists(snapshot_path):
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        with open(snapshot_path, "w", encoding="utf-8") as fh:
            json.dump(snapshot, fh, indent=2, ensure_ascii=False)
        pytest.skip("Snapshot written; re-run without FORZA_UPDATE_SNAPSHOTS to assert.")

    with open(snapshot_path, encoding="utf-8") as fh:
        expected = json.load(fh)

    assert snapshot == expected, (
        f"i18n strings for language={suffix!r} changed.\n"
        "To accept, rerun with FORZA_UPDATE_SNAPSHOTS=1."
    )
