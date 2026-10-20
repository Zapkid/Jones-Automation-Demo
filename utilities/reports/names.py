"""Short, unique names for artifacts (screenshots, traces)."""

from __future__ import annotations

from datetime import datetime

import pytest


def artifact_stem(item: pytest.Item, *, prefix: str = "") -> str:
    """Return a compact basename like ``CB2_20261020_160512_843``."""
    label: str = _case_label(item)
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return f"{prefix}{label}_{timestamp}"


def _case_label(item: pytest.Item) -> str:
    callspec = getattr(item, "callspec", None)
    if callspec is not None:
        param_id: str = callspec.id
        if "-" in param_id:
            return param_id.split("-", 1)[0]
        return param_id

    func_name: str = item.name.split("[", 1)[0]
    if func_name.startswith("test_"):
        func_name = func_name[5:]
    return func_name[:20]
