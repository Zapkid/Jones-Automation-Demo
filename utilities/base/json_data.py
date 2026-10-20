"""Load structured test data from JSON and JSONC files."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# Match string literals first so `//` inside values (e.g. "https://…") survives;
# only the comment alternatives are dropped.
_JSONC_TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/', re.DOTALL)


def _strip_jsonc_comments(text: str) -> str:
    return _JSONC_TOKEN.sub(lambda m: m.group(0) if m.group(0).startswith('"') else "", text)


def load_json_file(path: Path) -> Any:
    """Parse a ``.json`` or ``.jsonc`` file into Python objects."""
    text: str = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonc":
        text = _strip_jsonc_comments(text)
    return json.loads(text)
