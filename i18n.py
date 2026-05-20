"""Internationalisation strings loader.

The GUI uses parallel-array i18n: every UI string is exposed as a list
``[english_value, chinese_value]`` and the active language index selects
which entry to display. Historically this lived as 25 module-level lists
in ``constants.py``; this module loads them from JSON resource files at
``i18n/{en,zhcn}.json`` and exposes the same shape so existing call sites
in ``gui.py`` need no change.

Adding a new language is "drop in a JSON file with the same keys and add
it to ``LANGUAGES``"; the bundles are validated to share an identical
key set at import time so a missing key fails loudly.
"""

from __future__ import annotations

import json
import os
from typing import Final

_DIR: Final[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")

# Ordered list of supported languages. The index in this tuple is the
# value of ``constants.default_language`` / ``MainWindow.language``.
LANGUAGES: Final[tuple[str, ...]] = ("en", "zhcn")


def _load_bundle(name: str) -> dict[str, str]:
    path = os.path.join(_DIR, f"{name}.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_all() -> list[dict[str, str]]:
    bundles = [_load_bundle(name) for name in LANGUAGES]
    if bundles:
        canonical = set(bundles[0])
        for name, bundle in zip(LANGUAGES, bundles):
            missing = canonical - set(bundle)
            extra = set(bundle) - canonical
            if missing or extra:
                raise RuntimeError(
                    f"i18n bundle '{name}' has inconsistent keys: "
                    f"missing={sorted(missing)} extra={sorted(extra)}"
                )
    return bundles


BUNDLES: Final[list[dict[str, str]]] = _load_all()


def t(key: str) -> list[str]:
    """Return a parallel-array of translations for ``key``.

    The returned list is indexed by the position in :data:`LANGUAGES`,
    matching the existing call site shape ``constants.foo_txt[lang]``.

    Raises :class:`KeyError` for unknown keys (a typo we want to catch).
    """
    return [b[key] for b in BUNDLES]
