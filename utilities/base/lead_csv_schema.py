"""Validate the per-env ``valid_leads.csv`` / ``invalid_leads.csv`` rows before collection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from pages.jones.call_back.call_back_locators import CallBackLocators
from pages.jones.call_back.call_back_types import CallBackForm
from utilities.base.csv_data import load_csv_rows

LIST_SEPARATOR: Final[str] = "|"
_FORM_COLUMNS: Final[tuple[str, ...]] = (
    "name",
    "email",
    "phone",
    "company",
    "website",
    "employees",
)
_VALID_COLUMNS: Final[tuple[str, ...]] = ("id", "description", "markers", *_FORM_COLUMNS)
_INVALID_COLUMNS: Final[tuple[str, ...]] = (*_VALID_COLUMNS, "invalid_fields", "known_issue")
_EMPLOYEE_OPTIONS: Final[frozenset[str]] = frozenset({"1-10", "11-50", "51-500", "500+"})
_FIELD_IDS: Final[frozenset[str]] = frozenset(
    selector.element_id for selector in CallBackLocators().TEXT_FIELDS
)


class LeadCsvValidationError(ValueError):
    """Raised when a lead CSV fails schema checks."""


@dataclass(frozen=True)
class LeadRow:
    """One CSV row. ``form`` values may still contain the ``{run_id}`` token."""

    id: str
    description: str
    markers: tuple[str, ...]
    form: CallBackForm
    invalid_fields: frozenset[str] = frozenset()
    known_issue: str = ""


def _split(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(LIST_SEPARATOR) if part.strip())


def _check_columns(path: Path, rows: list[dict[str, str]], expected: tuple[str, ...]) -> None:
    if not rows:
        raise LeadCsvValidationError(f"{path}: has no data rows")
    columns = tuple(rows[0])
    if columns != expected:
        raise LeadCsvValidationError(f"{path}: columns {columns!r} != expected {expected!r}")


def _to_row(path: Path, raw: dict[str, str], seen: set[str]) -> LeadRow:
    row_id = raw["id"].strip()
    ref = f"{path.name} row {row_id or '?'}"
    if not row_id or row_id in seen:
        raise LeadCsvValidationError(f"{ref}: id must be non-empty and unique")
    seen.add(row_id)
    if not raw["description"].strip():
        raise LeadCsvValidationError(f"{ref}: description must be non-empty")
    if raw["employees"] not in _EMPLOYEE_OPTIONS:
        raise LeadCsvValidationError(
            f"{ref}: employees must be one of {sorted(_EMPLOYEE_OPTIONS)!r}"
        )
    return LeadRow(
        id=row_id,
        description=raw["description"].strip(),
        markers=_split(raw["markers"]),
        form=CallBackForm(
            name=raw["name"],
            email=raw["email"],
            phone=raw["phone"],
            company=raw["company"],
            website=raw["website"],
            employees=raw["employees"],
        ),
    )


def load_valid_leads(path: Path) -> list[LeadRow]:
    rows = load_csv_rows(path)
    _check_columns(path, rows, _VALID_COLUMNS)
    seen: set[str] = set()
    leads: list[LeadRow] = []
    for raw in rows:
        lead = _to_row(path, raw, seen)
        for required in ("name", "email", "phone"):
            if not getattr(lead.form, required).strip():
                raise LeadCsvValidationError(
                    f"{path.name} row {lead.id}: {required} is required for a valid lead"
                )
        leads.append(lead)
    return leads


def load_invalid_leads(path: Path) -> list[LeadRow]:
    rows = load_csv_rows(path)
    _check_columns(path, rows, _INVALID_COLUMNS)
    seen: set[str] = set()
    leads: list[LeadRow] = []
    for raw in rows:
        lead = _to_row(path, raw, seen)
        invalid = frozenset(_split(raw["invalid_fields"]))
        if not invalid or not invalid <= _FIELD_IDS:
            raise LeadCsvValidationError(
                f"{path.name} row {lead.id}: invalid_fields must be a non-empty subset of "
                f"{sorted(_FIELD_IDS)!r}"
            )
        leads.append(
            LeadRow(
                id=lead.id,
                description=lead.description,
                markers=lead.markers,
                form=lead.form,
                invalid_fields=invalid,
                known_issue=raw["known_issue"].strip(),
            )
        )
    return leads
