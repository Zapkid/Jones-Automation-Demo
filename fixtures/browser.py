"""Browser / context / page fixtures.

Layering:
  session scope: PlaywrightManager + Browser
  function scope: BrowserContext + Page (so each test starts clean, gets its
                  own trace, and we can attach a screenshot on failure).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from playwright.sync_api import BrowserContext, ConsoleMessage, Page

from utilities.allure.allure import attach_console_log
from utilities.base.envs import EnvConfig
from utilities.drivers.playwright_manager import LaunchOptions, PlaywrightManager
from utilities.reports.names import artifact_stem


@pytest.fixture(scope="session")
def launch_options(
    request: pytest.FixtureRequest,
    browser_name: str,
    env_config: EnvConfig,
) -> LaunchOptions:
    # `browser_name`, `--headed`, and `--slowmo` are provided by pytest-playwright
    # (browser engine selected via its `--browser` flag).
    return LaunchOptions(
        browser=browser_name,  # type: ignore[arg-type]
        headed=bool(request.config.getoption("--headed")),
        slowmo_ms=request.config.getoption("--slowmo"),
        trace=True,
        channel=env_config.browser_channel,
    )


@pytest.fixture(scope="session")
def playwright_manager(
    launch_options: LaunchOptions, env_config: EnvConfig
) -> Iterator[PlaywrightManager]:
    manager = PlaywrightManager(options=launch_options, reports_dir=env_config.reports_dir)
    manager.start()
    try:
        yield manager
    finally:
        manager.stop()


@pytest.fixture
def browser_context(playwright_manager: PlaywrightManager) -> Iterator[BrowserContext]:
    with playwright_manager.context() as context:
        yield context


@pytest.fixture
def console_messages() -> list[str]:
    """Browser console lines captured for the current test (attached to Allure)."""
    return []


@pytest.fixture
def page(
    request: pytest.FixtureRequest,
    playwright_manager: PlaywrightManager,
    browser_context: BrowserContext,
    console_messages: list[str],
) -> Iterator[Page]:
    def _on_console(msg: ConsoleMessage) -> None:
        console_messages.append(f"[{msg.type}] {msg.text}")

    trace_name = artifact_stem(request.node)

    def _keep_trace() -> bool:
        # Traces are large; keep them for failures unless --keep-traces is passed.
        report = getattr(request.node, "rep_call", None)
        failed: bool = report is not None and report.failed
        return failed or bool(request.config.getoption("--keep-traces"))

    with playwright_manager.page(
        browser_context, trace_name=trace_name, keep_trace=_keep_trace
    ) as page:
        page.on("console", _on_console)
        yield page
        attach_console_log(console_messages)
