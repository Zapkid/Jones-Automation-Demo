"""Load tabular test data from CSV files."""

from __future__ import annotations

import csv
from pathlib import Path

_COMMENT_PREFIX: str = "#"


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    """Parse a CSV with a header row into dicts; lines starting with ``#`` are comments.

    Cell values are kept verbatim (no stripping), so whitespace-only data survives.
    """
    with path.open(encoding="utf-8", newline="") as handle:
        lines: list[str] = [line for line in handle if not line.startswith(_COMMENT_PREFIX)]
    reader = csv.DictReader(lines)
    rows: list[dict[str, str]] = []
    for line_no, row in enumerate(reader, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"{path}: data row {line_no} has a different column count")
        rows.append(dict(row))
    return rows
