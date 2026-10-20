"""Module hooks for call_back tests — parametrize cases from JSONC."""

from __future__ import annotations

from typing import Any

import pytest

from fixtures.call_back import load_call_back_cases


def _marks_for(case: dict[str, Any]) -> list[pytest.MarkDecorator]:
    marks: list[pytest.MarkDecorator] = [
        getattr(pytest.mark, marker) for marker in case.get("markers", [])
    ]
    if case.get("envs"):
        marks.append(pytest.mark.supported_envs(*case["envs"]))
    return marks


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize ``case`` from ``resources/test_data/call_back_cases.jsonc``."""
    if "case" not in metafunc.fixturenames:
        return
    params = [
        pytest.param(case, id=str(case["id"]), marks=_marks_for(case))
        for case in load_call_back_cases()
    ]
    metafunc.parametrize("case", params)
