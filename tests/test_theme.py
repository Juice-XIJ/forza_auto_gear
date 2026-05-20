"""Tests for the theme/font helpers."""

from __future__ import annotations

import pytest

import theme


def test_resolve_mono_family_returns_string(tk_root):
    family = theme.resolve_mono_family()
    assert isinstance(family, str)
    assert family  # non-empty


def test_log_font_is_three_tuple(tk_root):
    f = theme.log_font()
    assert isinstance(f, tuple) and len(f) == 3
    family, size, weight = f
    assert isinstance(family, str)
    assert isinstance(size, int) and size > 0
    assert weight in {"normal", "bold", "bold italic", "italic"}


@pytest.mark.parametrize("role", ["h1", "h2", "display", "log"])
def test_font_role_resolves(tk_root, role):
    f = theme.font(role)
    assert isinstance(f, tuple) and len(f) == 3


def test_font_unknown_role_raises():
    with pytest.raises(KeyError):
        theme.font("does-not-exist")


def test_fallback_when_no_preferred_family_available(tk_root, monkeypatch):
    # Force every preferred family to be "missing".
    monkeypatch.setattr(theme, "_MONO_PREFERENCES", ())
    family = theme.resolve_mono_family()
    assert family == "TkFixedFont"


def test_apply_global_ttk_theme_configures_named_styles(tk_root):
    style = theme.apply_global_ttk_theme(tk_root)
    # Each named style must be queryable; ttk.Style.configure with no
    # values returns the current settings dict.
    for name in theme.STYLES.values():
        opts = style.configure(name)
        assert opts is not None, f"style {name!r} was not configured"


def test_apply_global_ttk_theme_is_idempotent(tk_root):
    style1 = theme.apply_global_ttk_theme(tk_root)
    style2 = theme.apply_global_ttk_theme(tk_root)
    # Both calls should target the same ttk.Style instance per root and
    # leave the configuration intact.
    assert style1.configure(theme.STYLES["label"]) == style2.configure(theme.STYLES["label"])
