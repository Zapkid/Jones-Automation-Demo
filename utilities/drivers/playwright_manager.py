"""Playwright lifecycle wrapper.

Wraps browser/context/page creation so fixtures don't need to know the launch
flags or trace settings. Keeps video/trace paths under ``reports/``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

BrowserName = Literal["chromium", "firefox", "webkit"]


@dataclass(frozen=True)
class LaunchOptions:
    browser: BrowserName = "chromium"
    headed: bool = False
    slowmo_ms: int = 0
    viewport_width: int = 1440
    viewport_height: int = 900
    record_video: bool = False
    trace: bool = True
    channel: str | None = None


class PlaywrightManager:
    """Owns the playwright + browser handles for a single fixture scope."""

    def __init__(self, options: LaunchOptions, reports_dir: Path) -> None:
        self._options = options
        self._reports_dir = reports_dir
        for sub in ("traces", "videos", "screenshots"):
            (self._reports_dir / sub).mkdir(parents=True, exist_ok=True)

        self._pw: Playwright | None = None
        self._browser: Browser | None = None

    def start(self) -> Browser:
        self._pw = sync_playwright().start()
        launcher = getattr(self._pw, self._options.browser)
        launch_kwargs: dict[str, object] = {
            "headless": not self._options.headed,
            "slow_mo": self._options.slowmo_ms,
        }
        if self._options.channel:
            launch_kwargs["channel"] = self._options.channel
        self._browser = launcher.launch(**launch_kwargs)  # type: ignore[arg-type]
        return self._browser

    def stop(self) -> None:
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._pw:
            self._pw.stop()
            self._pw = None

    @contextmanager
    def context(self) -> Iterator[BrowserContext]:
        if self._browser is None:
            raise RuntimeError("PlaywrightManager.start() must be called first")

        context = self._browser.new_context(
            viewport={
                "width": self._options.viewport_width,
                "height": self._options.viewport_height,
            },
            record_video_dir=(
                str(self._reports_dir / "videos") if self._options.record_video else None
            ),
        )
        if self._options.trace:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
        try:
            yield context
        finally:
            context.close()

    @contextmanager
    def page(
        self,
        context: BrowserContext,
        trace_name: str | None = None,
        *,
        keep_trace: Callable[[], bool] = lambda: True,
    ) -> Iterator[Page]:
        page = context.new_page()
        try:
            yield page
        finally:
            if self._options.trace:
                trace_path: str | None = None
                if trace_name and keep_trace():
                    trace_path = str(self._reports_dir / "traces" / f"{trace_name}.zip")
                try:
                    context.tracing.stop(path=trace_path)
                except Exception:
                    print(f"Error stopping trace: {trace_path}")
            page.close()
