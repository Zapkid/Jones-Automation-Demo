"""BasePage — thin wrapper around Playwright Page with shared behaviours.

Every concrete page object inherits from this so we centralize navigation,
default timeouts, and shared interactions (text fields, dropdowns).
"""

from __future__ import annotations

from typing import Final, Literal

import allure
from playwright.sync_api import Locator, Page, expect

DEFAULT_TIMEOUT_MS: Final[int] = 15_000

WaitUntil = Literal["commit", "domcontentloaded", "load", "networkidle"]


class BasePage:
    """Common Playwright operations exposed to feature page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.page.set_default_timeout(DEFAULT_TIMEOUT_MS)

    # ---------- navigation ---------- #

    @allure.step("Open URL: {url}")
    def goto(self, url: str, *, wait_until: WaitUntil = "domcontentloaded") -> None:
        self.page.goto(url, wait_until=wait_until)

    # ---------- locators ---------- #

    def by_id_or_label(self, element_id: str, label: str) -> Locator:
        """Resolve a form control by ``id``, falling back to its exact accessible label."""
        return (
            self.page.locator(f"#{element_id}").or_(self.page.get_by_label(label, exact=True)).first
        )

    # ---------- interaction helpers ---------- #

    @allure.step("Click element: {what}")
    def click(self, locator: Locator, what: str, *, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
        expect(locator).to_be_visible(timeout=timeout_ms)
        locator.click(timeout=timeout_ms)

    @allure.step("Fill {what} with {value!r}")
    def fill(
        self,
        locator: Locator,
        value: str,
        what: str,
        *,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
    ) -> None:
        expect(locator).to_be_visible(timeout=timeout_ms)
        locator.fill(value, timeout=timeout_ms)
        expect(locator).to_have_value(value, timeout=timeout_ms)

    @allure.step("Select {option!r} in {what}")
    def select(self, locator: Locator, option: str, what: str) -> None:
        """Pick an option from a native ``<select>`` or a custom listbox dropdown."""
        expect(locator).to_be_visible()
        tag: str = locator.evaluate("el => el.tagName.toLowerCase()")
        if tag == "select":
            locator.select_option(label=option)
            return
        locator.click()
        self.page.get_by_role("option", name=option, exact=True).first.click()

    def selected_option_text(self, locator: Locator) -> str:
        """Visible text of the current choice in a native or custom dropdown."""
        return str(
            locator.evaluate(
                "el => el.tagName.toLowerCase() === 'select'"
                " ? el.options[el.selectedIndex].text : el.textContent"
            )
        ).strip()
