"""Pytest entry point.

We expose plugin hooks here (Allure metadata, env-marker filtering, failure
artifact capture) and import the reusable fixture modules so tests can pull
them by name.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any

import pytest

# Re-export fixtures from the dedicated modules so pytest discovers them.
pytest_plugins = (
    "fixtures.env",
    "fixtures.browser",
    "fixtures.call_back",
)

from playwright.sync_api import Page  # noqa: E402  (after pytest_plugins on purpose)

from utilities.allure.allure import attach_failure_artifacts  # noqa: E402
from utilities.base.envs import EnvConfig, resolve  # noqa: E402
from utilities.reports.names import artifact_stem  # noqa: E402
from utilities.reports.post_process import (  # noqa: E402
    write_categories,
    write_environment_properties,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ALLURE_RESULTS = REPO_ROOT / "reports" / "allure_results"
ALLURE_REPORT = REPO_ROOT / "reports" / "allure_report"
logger = logging.getLogger(__name__)


# ---------- Allure metadata ---------- #


def pytest_configure(config: pytest.Config) -> None:
    ALLURE_RESULTS.mkdir(parents=True, exist_ok=True)
    write_categories(ALLURE_RESULTS)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Drop environment.properties so Allure shows env + base URL."""
    env = resolve(session.config.getoption("--env"))
    write_environment_properties(ALLURE_RESULTS, env.env.value, env.base_url)


def pytest_unconfigure(config: pytest.Config) -> None:
    """Generate the static Allure HTML report after xdist workers have shut down."""
    if getattr(config, "workerinput", None):
        return
    if config.getoption("--no-allure-report"):
        return
    if not any(ALLURE_RESULTS.glob("*-result.json")):
        return

    from utilities.allure.allure import generate_report

    try:
        generate_report(ALLURE_RESULTS, ALLURE_REPORT)
        logger.info("Allure report generated at %s", ALLURE_REPORT)
    except (FileNotFoundError, OSError, subprocess.CalledProcessError) as exc:
        logger.warning("Allure report generation skipped: %s", exc)


# ---------- env-marker filtering ---------- #


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip tests whose `supported_envs(...)` marker doesn't include the active env."""
    env = resolve(config.getoption("--env")).env.value
    skip_other_env = pytest.mark.skip(reason=f"not supported on env={env}")
    for item in items:
        marker = item.get_closest_marker("supported_envs")
        if marker is not None and env not in marker.args:
            item.add_marker(skip_other_env)


# ---------- failure artifact capture ---------- #


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]):  # noqa: ANN201
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    # Read by the `page` fixture at teardown to decide whether to keep the trace.
    item.rep_call = report  # type: ignore[attr-defined]
    if not report.failed:
        return

    funcargs: dict[str, Any] = getattr(item, "funcargs", {})
    page: Page | None = funcargs.get("page")
    env_config: EnvConfig | None = funcargs.get("env_config")
    if page is None or env_config is None:
        return
    attach_failure_artifacts(page, artifact_stem(item), env_config.reports_dir)
