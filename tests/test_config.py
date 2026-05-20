"""Tests for config management: naming, loading, and saving car configurations.

Covers get_config_name (v1/v2/invalid), load_config field population,
and handling of missing/partial config data.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import types
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import constants
import helper
from constants import ConfigVersion
from forza import Forza


def _make_forza():
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="test")
    f = Forza(pool, packet_format=constants.packet_format)
    return f


# === Config name generation ===

def test_config_name_v2_format():
    """v2 config name includes ordinal, perf, and drivetrain."""
    fake = types.SimpleNamespace(ordinal=12345, car_perf=800, car_drivetrain=1)
    name = helper.get_config_name(fake, ConfigVersion.v2)
    assert name == "12345-800-1.json"


def test_config_name_v1_format():
    """v1 config name is just ordinal."""
    fake = types.SimpleNamespace(ordinal=12345)
    name = helper.get_config_name(fake, ConfigVersion.v1)
    assert name == "12345.json"


def test_config_name_invalid_version_returns_none():
    """Invalid config version logs warning and returns None (original behavior)."""
    warnings = []
    fake = types.SimpleNamespace(
        ordinal=123, car_perf=800, car_drivetrain=1,
        logger=types.SimpleNamespace(warning=lambda msg: warnings.append(msg)),
    )
    result = helper.get_config_name(fake, config_version="bogus")
    assert result is None
    assert len(warnings) == 1


# === Config version enum ===

def test_config_version_values_are_ints():
    """ConfigVersion members have int values, not tuples."""
    assert ConfigVersion.v1.value == 1
    assert ConfigVersion.v2.value == 2
    assert isinstance(ConfigVersion.v1.value, int)


def test_config_version_lookup_by_value():
    """Can look up ConfigVersion by integer value."""
    assert ConfigVersion(1) is ConfigVersion.v1
    assert ConfigVersion(2) is ConfigVersion.v2


# === Load config ===

def test_load_config_populates_all_fields():
    """load_config fills ordinal, perf, class, drivetrain, gear data."""
    f = _make_forza()
    config = {
        'version': 'v2',
        'ordinal': 99999,
        'perf': 900,
        'class': 5,
        'drivetrain': 1,
        'minGear': 2,
        'maxGear': 7,
        'gear_ratios': {'2': 0.5, '3': 0.8},
        'rpm_torque_map': {'2': {'min_rpm_index': 0, 'max_rpm_index': 100}},
        'shift_point': {'2': {'rpmo': 6500, 'speed': 100}},
        'records': [{'gear': 2, 'rpm': 5000}],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = "test_config.json"
        with open(os.path.join(tmpdir, config_path), "w") as fh:
            json.dump(config, fh)

        f.config_folder = tmpdir
        helper.load_config(f, config_path)

    assert f.ordinal == 99999
    assert f.car_perf == 900
    assert f.car_class == 5
    assert f.car_drivetrain == 1
    assert f.minGear == 2
    assert f.maxGear == 7
    assert 2 in f.gear_ratios
    assert 2 in f.shift_point
    assert len(f.records) == 1


def test_load_config_handles_missing_optional_fields():
    """load_config doesn't crash when optional fields are absent."""
    f = _make_forza()
    config = {'ordinal': 11111}

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = "sparse.json"
        with open(os.path.join(tmpdir, config_path), "w") as fh:
            json.dump(config, fh)

        f.config_folder = tmpdir
        helper.load_config(f, config_path)

    assert f.ordinal == 11111
    # Other fields retain defaults
    assert f.minGear == 1
    assert f.maxGear == 5
