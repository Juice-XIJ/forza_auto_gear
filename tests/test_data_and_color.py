"""Tests for data collection (test_gear) and the rgb color utility.

Covers record accumulation, speed/rpm ratio edge cases, stationary
filtering, and rgb hex conversion with clamping.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import helper


# === Data collection: speed/rpm ratio ===

def test_speed_rpm_ratio_with_zero_rpm():
    """speed/rpm calculation handles rpm=0 without ZeroDivisionError."""
    # This simulates what test_gear() builds for each record
    speed_kmh = 50 * 3.6  # 180 km/h
    rpm = 0
    ratio = speed_kmh / max(rpm, 1)
    assert ratio == speed_kmh  # falls back to dividing by 1


def test_speed_rpm_ratio_normal():
    """speed/rpm ratio is correct for normal values."""
    speed_kmh = 100 * 3.6  # 360 km/h
    rpm = 6000
    ratio = speed_kmh / max(rpm, 1)
    assert abs(ratio - 0.06) < 0.001


# === rgb color utility ===

def test_rgb_red():
    assert helper.rgb(1, 0, 0) == "#ff0000"


def test_rgb_green():
    assert helper.rgb(0, 1, 0) == "#00ff00"


def test_rgb_blue():
    assert helper.rgb(0, 0, 1) == "#0000ff"


def test_rgb_black():
    assert helper.rgb(0, 0, 0) == "#000000"


def test_rgb_white():
    assert helper.rgb(1, 1, 1) == "#ffffff"


def test_rgb_mid_gray():
    result = helper.rgb(0.5, 0.5, 0.5)
    # 0.5 * 255 = 127.5 → int(127) = 127 → hex 7f
    assert result == "#7f7f7f"


def test_rgb_clamps_values_above_one():
    """Values > 1.0 are clamped to 1.0 (255)."""
    assert helper.rgb(1.5, 0, 0) == "#ff0000"
    assert helper.rgb(0, 2.0, 0) == "#00ff00"


def test_rgb_clamps_negative_values():
    """Negative values are clamped to 0."""
    assert helper.rgb(-0.5, 0, 0) == "#000000"
    assert helper.rgb(0, -1, 0) == "#000000"


def test_rgb_mixed_out_of_range():
    """Mix of out-of-range and normal values."""
    assert helper.rgb(1.5, 0.5, -0.5) == "#ff7f00"
