"""Validate ``call_back_cases.jsonc`` before collection."""

from __future__ import annotations

from typing import Any

from pages.jones.call_back.call_back_types import SubmitOutcome
from utilities.base.envs import Env

_REQUIRED_FORM_KEYS: tuple[str, ...] = ("name", "email", "phone", "company", "website")
_OPTIONAL_FORM_KEYS: tuple[str, ...] = ("employees",)
_VALID_OUTCOMES: frozenset[str] = frozenset(o.value for o in SubmitOutcome)
_VALID_ENVS: frozenset[str] = frozenset(e.value for e in Env)


class CallBackCaseValidationError(ValueError):
    """Raised when a case or the cases file fails schema checks."""


def _require_mapping(value: Any, *, ref: str, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CallBackCaseValidationError(f"{ref}: {field} must be an object")
    return value


def _require_non_empty_str(value: Any, *, ref: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CallBackCaseValidationError(f"{ref}: {field} must be a non-empty string")
    return value


def _require_list_of_str(value: Any, *, ref: str, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise CallBackCaseValidationError(f"{ref}: {field} must be a list of strings")
    return value


def _validate_form(form: Any, *, ref: str) -> None:
    form_map = _require_mapping(form, ref=ref, field="form")
    unknown = set(form_map) - set(_REQUIRED_FORM_KEYS) - set(_OPTIONAL_FORM_KEYS)
    if unknown:
        raise CallBackCaseValidationError(f"{ref}: form has unknown keys {sorted(unknown)!r}")
    for key in _REQUIRED_FORM_KEYS:
        _require_non_empty_str(form_map.get(key), ref=ref, field=f"form.{key}")
    if "employees" in form_map:
        _require_non_empty_str(form_map["employees"], ref=ref, field="form.employees")


def _validate_expected(expected: Any, *, ref: str) -> None:
    expected_map = _require_mapping(expected, ref=ref, field="expected")
    outcome = expected_map.get("outcome")
    if not isinstance(outcome, str) or outcome not in _VALID_OUTCOMES:
        raise CallBackCaseValidationError(
            f"{ref}: expected.outcome must be one of {sorted(_VALID_OUTCOMES)!r}"
        )
    invalid_field = expected_map.get("invalid_field")
    if invalid_field is None:
        return
    if outcome != SubmitOutcome.STAYS_ON_FORM.value:
        raise CallBackCaseValidationError(
            f"{ref}: expected.invalid_field only applies to outcome 'stays_on_form'"
        )
    _require_non_empty_str(invalid_field, ref=ref, field="expected.invalid_field")


def validate_call_back_case(case: Any, *, index: int) -> dict[str, Any]:
    """Validate one case dict; return it unchanged when valid."""
    if not isinstance(case, dict):
        raise CallBackCaseValidationError(f"case at index {index} must be an object")

    raw_id = case.get("id")
    ref = f"case {raw_id!r}" if isinstance(raw_id, str) and raw_id else f"case at index {index}"

    _require_non_empty_str(case.get("id"), ref=ref, field="id")
    _require_non_empty_str(case.get("description"), ref=ref, field="description")
    _require_list_of_str(case.get("markers", []), ref=ref, field="markers")
    envs = _require_list_of_str(case.get("envs", []), ref=ref, field="envs")
    bad_envs = set(envs) - _VALID_ENVS
    if bad_envs:
        raise CallBackCaseValidationError(f"{ref}: envs has unknown values {sorted(bad_envs)!r}")
    _validate_form(case.get("form"), ref=ref)
    _validate_expected(case.get("expected"), ref=ref)
    return case


def validate_call_back_cases_document(raw: Any) -> list[dict[str, Any]]:
    """Validate the full JSONC document and return the cases list."""
    if not isinstance(raw, dict):
        raise CallBackCaseValidationError("call_back_cases root must be an object")
    cases_raw = raw.get("cases")
    if not isinstance(cases_raw, list) or not cases_raw:
        raise CallBackCaseValidationError("call_back_cases.cases must be a non-empty list")

    validated: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, case in enumerate(cases_raw):
        valid_case = validate_call_back_case(case, index=index)
        case_id = str(valid_case["id"])
        if case_id in seen_ids:
            raise CallBackCaseValidationError(f"duplicate case id {case_id!r}")
        seen_ids.add(case_id)
        validated.append(valid_case)
    return validated
