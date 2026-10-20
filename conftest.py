"""Root conftest — owns CLI options so they're available at config-load time.

Fixture and hook implementations live under `fixtures/` and `tests/conftest.py`;
this file only declares the shared CLI flags.
"""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("jones-aqa")
    group.addoption(
        "--env",
        action="store",
        default=None,
        help="Target env (prod). Defaults to $ENV or 'prod'.",
    )
    group.addoption(
        "--keep-traces",
        action="store_true",
        default=False,
        help="Keep Playwright traces for passing tests too (default: failures only).",
    )
    group.addoption(
        "--no-allure-report",
        action="store_true",
        default=False,
        help="Skip generating the static Allure HTML report after the run.",
    )
    # --headed, --slowmo, and --browser are registered by pytest-playwright;
    # re-declaring them raises `argparse.ArgumentError: conflicting option string`.


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: pytest.Config) -> None:
    """`-n=1` enables xdist with no parallelism and fragile worker teardown; run in-process."""
    if getattr(config.option, "numprocesses", None) == 1:
        config.option.numprocesses = 0
        config.option.dist = "no"
        config.option.tx = []
