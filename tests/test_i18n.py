"""Tests for the i18n bundle loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import i18n


def test_bundles_have_identical_keys():
    """All language bundles must share the exact same key set."""
    canonical = set(i18n.BUNDLES[0])
    for name, bundle in zip(i18n.LANGUAGES, i18n.BUNDLES):
        assert set(bundle) == canonical, f"bundle {name!r} has different keys"


def test_t_returns_parallel_array():
    values = i18n.t("speed_txt")
    assert isinstance(values, list)
    assert len(values) == len(i18n.LANGUAGES)
    assert values[0] == "Speed"
    assert values[1] == "速度"


def test_t_missing_key_raises():
    with pytest.raises(KeyError):
        i18n.t("definitely_not_a_real_key")


def test_locales_directory_contains_one_json_per_language():
    locales = Path(__file__).resolve().parent.parent / "locales"
    files = {p.stem for p in locales.glob("*.json")}
    assert set(i18n.LANGUAGES).issubset(files), (
        f"expected one JSON per language; got {sorted(files)}"
    )


def test_loader_rejects_mismatched_bundles(tmp_path, monkeypatch):
    """If two bundles have different key sets, _load_all must raise."""
    bad_en = tmp_path / "en.json"
    bad_zh = tmp_path / "zhcn.json"
    bad_en.write_text(json.dumps({"a": "1", "b": "2"}), encoding="utf-8")
    bad_zh.write_text(json.dumps({"a": "uno"}), encoding="utf-8")  # missing 'b'

    monkeypatch.setattr(i18n, "_DIR", str(tmp_path))
    with pytest.raises(RuntimeError, match="inconsistent keys"):
        i18n._load_all()
