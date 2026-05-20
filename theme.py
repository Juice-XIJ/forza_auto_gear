"""Lightweight theme / font helpers shared by ``gui.py``.

Centralises font resolution (so we can pick a sensible monospaced font
that actually exists on the current platform) and the per-role font
tuples used in the GUI. This is a small standalone module so it can be
imported by ``gui.py`` today and folded into a ``gui.theme`` submodule
in a future package split with no API change.

``apply_global_ttk_theme`` configures the ``ttk.Style`` for the project
so that any future migration of widgets from ``tkinter`` to ``ttk`` (the
``ui-ttk-theme`` follow-up item) only needs to pick up the named style
rather than re-specify colours per widget.
"""

from __future__ import annotations

import tkinter.font as tkfont
import tkinter.ttk as ttk
from typing import Iterable

import constants


_MONO_PREFERENCES: tuple[str, ...] = (
    "Cascadia Mono",
    "Cascadia Code",
    "JetBrains Mono",
    "Consolas",
    "Menlo",
    "Monaco",  # macOS — still tried so existing behavior is preserved there
    "DejaVu Sans Mono",
    "Courier New",
)


def _first_available(candidates: Iterable[str], fallback: str) -> str:
    """Return the first font family from ``candidates`` known to Tk.

    Falls back to ``fallback`` (a Tk named font, e.g. ``"TkFixedFont"``)
    when none of the candidates are installed.
    """
    try:
        available = set(tkfont.families())
    except Exception:
        # Tk not initialised yet; the caller will resolve again later.
        return fallback
    for family in candidates:
        if family in available:
            return family
    return fallback


def resolve_mono_family() -> str:
    """Pick the best available monospaced font on this machine."""
    return _first_available(_MONO_PREFERENCES, fallback="TkFixedFont")


def log_font() -> tuple[str, int, str]:
    """Font tuple for the GUI log pane."""
    return (resolve_mono_family(), 10, "normal")


# Named font roles for the rest of the GUI. These are intentionally
# returned by helpers (not constants) so they re-resolve after Tk has
# initialised. The "h*" naming follows web/typographic convention.
def h1() -> tuple[str, int, str]:
    return ("Helvetica", 20, "bold")


def h2() -> tuple[str, int, str]:
    return ("Helvetica", 15, "bold")


def display() -> tuple[str, int, str]:
    return ("Helvetica", 35, "bold italic")


FONTS = {
    "h1": h1,
    "h2": h2,
    "display": display,
    "log": log_font,
}


def font(role: str) -> tuple[str, int, str]:
    """Resolve a named font role to a Tk font tuple.

    Raises ``KeyError`` for unknown roles (a typo we want to catch).
    """
    return FONTS[role]()


# --- Centralised ttk theme ---------------------------------------------

#: Named ttk style classes the rest of the codebase should target. Adding
#: a widget to one of these styles is preferred over per-widget ``bg=``
#: / ``fg=`` arguments — change colors here and every styled widget moves.
STYLES = {
    "frame": "Forza.TFrame",
    "label": "Forza.TLabel",
    "button": "Forza.TButton",
    "treeview": "Treeview",  # Treeview already has a global style configured in gui_frames
}


def apply_global_ttk_theme(root) -> ttk.Style:
    """Configure the project's ``ttk.Style`` family on the given root.

    Idempotent — safe to call multiple times. Returns the ``ttk.Style``
    object so callers can register additional styles if needed.

    The migration target is to use ``ttk.Frame(style="Forza.TFrame")``
    etc. throughout the GUI; today most widgets are still ``tkinter.*``
    with explicit ``bg=``/``fg=`` and pick up these styles only via
    ``ttk.Treeview``. See plan.md "ui-ttk-theme" follow-up.
    """
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        STYLES["frame"],
        background=constants.background_color,
        borderwidth=0,
        relief="groove",
    )
    style.configure(
        STYLES["label"],
        background=constants.background_color,
        foreground=constants.text_color,
        font=h2(),
    )
    style.configure(
        STYLES["button"],
        background=constants.background_color,
        foreground=constants.text_color,
        borderwidth=3,
        focusthickness=3,
        focuscolor=constants.text_color,
    )
    # Treeview colors (these were previously set inline in
    # ``set_shift_point_frame``; centralised here so a future ttk-theme
    # migration only has to edit this module).
    style.configure(
        "Treeview",
        background=constants.background_color,
        foreground=constants.text_color,
        fieldbackground=constants.background_color,
    )
    style.map(
        "Treeview",
        background=[("selected", "#BFBFBF")],
        foreground=[("selected", "black")],
        fieldbackground=[("selected", "black")],
    )
    return style
