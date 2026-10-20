"""Verifications layer.

Tests must NEVER use a raw `assert` — every check goes through this class so
failure messages stay consistent and Allure captures each step.
"""

from __future__ import annotations

import re
from typing import Any

import allure


class Verifications:
    """Allure-instrumented assertion helpers.

    Each method:
      * Runs inside an ``@allure.step`` block so it appears in the report.
      * Raises ``AssertionError`` with a clear, contextual message on failure.
    """

    def equals(self, actual: Any, expected: Any, what: str) -> None:
        with allure.step(f"Verify {what} == {expected!r}"):
            if actual != expected:
                raise AssertionError(f"{what}: expected {expected!r} but got {actual!r}")

    def is_true(self, condition: bool, what: str) -> None:
        with allure.step(f"Verify {what} is true"):
            if not condition:
                raise AssertionError(f"Expected condition to be true: {what}")

    def is_false(self, condition: bool, what: str) -> None:
        with allure.step(f"Verify {what} is false"):
            if condition:
                raise AssertionError(f"Expected condition to be false: {what}")

    def matches(self, actual: str, pattern: str, what: str) -> None:
        with allure.step(f"Verify {what} matches /{pattern}/"):
            if not re.search(pattern, actual, re.IGNORECASE):
                raise AssertionError(f"{what}: {actual!r} does not match /{pattern}/i")
