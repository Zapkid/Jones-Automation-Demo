"""Module hooks for call_back tests — parametrize from JSONC and the per-env CSVs."""

from __future__ import annotations

from typing import Any

import pytest

from fixtures.call_back import (
    load_call_back_cases,
    load_env_invalid_leads,
    load_env_valid_leads,
)
from utilities.base.envs import resolve
from utilities.base.lead_csv_schema import LeadRow


def _marks_for(case: dict[str, Any]) -> list[pytest.MarkDecorator]:
    marks: list[pytest.MarkDecorator] = [
        getattr(pytest.mark, marker) for marker in case.get("markers", [])
    ]
    if case.get("envs"):
        marks.append(pytest.mark.supported_envs(*case["envs"]))
    return marks


def _lead_marks(lead: LeadRow) -> list[pytest.MarkDecorator]:
    marks: list[pytest.MarkDecorator] = [getattr(pytest.mark, marker) for marker in lead.markers]
    if lead.known_issue:
        # Strict: once the site starts rejecting this input, XPASS fails the run so the row
        # gets its known_issue cleared instead of silently staying an expected failure.
        marks.append(pytest.mark.xfail(reason=f"Known issue: {lead.known_issue}", strict=True))
    return marks


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize ``case`` (JSONC) and ``valid_lead`` / ``invalid_lead`` (per-env CSV)."""
    if "case" in metafunc.fixturenames:
        params = [
            pytest.param(case, id=str(case["id"]), marks=_marks_for(case))
            for case in load_call_back_cases()
        ]
        metafunc.parametrize("case", params)

    env_config = resolve(metafunc.config.getoption("--env"))
    if "valid_lead" in metafunc.fixturenames:
        metafunc.parametrize(
            "valid_lead",
            [
                pytest.param(lead, id=lead.id, marks=_lead_marks(lead))
                for lead in load_env_valid_leads(env_config)
            ],
        )
    if "invalid_lead" in metafunc.fixturenames:
        metafunc.parametrize(
            "invalid_lead",
            [
                pytest.param(lead, id=lead.id, marks=_lead_marks(lead))
                for lead in load_env_invalid_leads(env_config)
            ],
        )
