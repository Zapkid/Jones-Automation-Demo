"""Page object for the post-submit thank-you page."""

from __future__ import annotations

import logging
import re

import allure
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PWTimeoutError

from pages.base.base_page import BasePage
from pages.jones.thank_you.thank_you_locators import ThankYouLocators

logger = logging.getLogger(__name__)

_THANK_YOU_TIMEOUT_MS: int = 15_000


class ThankYouPage(BasePage):
    """Detects arrival on the thank-you page by URL or heading."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.loc = ThankYouLocators()

    def _heading(self) -> str | None:
        heading = self.page.get_by_role(
            "heading", name=re.compile(self.loc.HEADING_PATTERN, re.IGNORECASE)
        )
        if heading.count() == 0:
            return None
        return heading.first.inner_text().strip()

    @allure.step("Wait for the thank-you page")
    def wait_until_reached(self, *, timeout_ms: int = _THANK_YOU_TIMEOUT_MS) -> bool:
        """True once the URL or a heading signals the thank-you page."""
        url_re = re.compile(self.loc.URL_PATTERN, re.IGNORECASE)
        heading_re = re.compile(self.loc.HEADING_PATTERN, re.IGNORECASE)
        try:
            self.page.wait_for_function(
                """([urlSrc, headingSrc]) => {
                    if (new RegExp(urlSrc, 'i').test(location.href)) return true;
                    const re = new RegExp(headingSrc, 'i');
                    return [...document.querySelectorAll('h1, h2, [role=heading]')]
                        .some(h => re.test(h.textContent || ''));
                }""",
                arg=[url_re.pattern, heading_re.pattern],
                timeout=timeout_ms,
            )
        except PWTimeoutError:
            return False
        self.page.wait_for_load_state("domcontentloaded")
        return True

    @property
    def heading(self) -> str | None:
        return self._heading()

    @allure.step("Write arrival message to console.log")
    def log_arrival(self, message: str) -> None:
        """Emit the message to the browser console *and* the Python test log."""
        self.page.evaluate("msg => console.log(msg)", message)
        logger.info(message)
