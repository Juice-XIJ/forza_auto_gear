"""Characterization snapshot of the MainWindow widget tree.

This pins the observable widget structure of ``gui.MainWindow`` so that any
structural refactor either preserves the visible layout *or* forces a
conscious snapshot update.

Run with ``FORZA_UPDATE_SNAPSHOTS=1 pytest tests/test_baseline_widget_tree.py``
to regenerate the snapshot after a deliberate change.
"""

from __future__ import annotations

import json
import os
import re

import pytest

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "snapshots")
SNAPSHOT_PATH = os.path.join(SNAPSHOT_DIR, "widget_tree.json")


# Tk auto-generates internal widget paths like ".!frame.!label2". We strip
# the trailing digits so two structurally-identical layouts compare equal.
_PATH_DIGIT_RE = re.compile(r"\d+")


def _normalise(path: str) -> str:
    return _PATH_DIGIT_RE.sub("#", path)


def _walk(widget):
    """Yield (normalised_path, class_name, grid_info) for every descendant."""
    for child in widget.winfo_children():
        info = child.grid_info() if hasattr(child, "grid_info") else {}
        row = info.get("row")
        col = info.get("column")
        yield (
            _normalise(str(child)),
            child.winfo_class(),
            None if row is None else int(row),
            None if col is None else int(col),
        )
        yield from _walk(child)


def test_widget_tree_snapshot(main_window_factory):
    win = main_window_factory()
    win.root.update_idletasks()
    tree = sorted(_walk(win.root))

    if os.environ.get("FORZA_UPDATE_SNAPSHOTS") == "1" or not os.path.exists(SNAPSHOT_PATH):
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        with open(SNAPSHOT_PATH, "w", encoding="utf-8") as fh:
            json.dump(tree, fh, indent=2)
        pytest.skip("Snapshot written; re-run without FORZA_UPDATE_SNAPSHOTS to assert.")

    with open(SNAPSHOT_PATH, encoding="utf-8") as fh:
        expected = json.load(fh)

    # JSON tuples come back as lists.
    expected_norm = [tuple(item) for item in expected]
    assert tree == expected_norm, (
        "Widget tree changed.\nTo accept, rerun with FORZA_UPDATE_SNAPSHOTS=1."
    )
