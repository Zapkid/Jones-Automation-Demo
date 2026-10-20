"""Page object for the landing page "Request a call back" lead form."""

from __future__ import annotations

import time

import allure
from playwright.sync_api import Locator, Page

from pages.base.base_page import BasePage
from pages.jones.call_back.call_back_locators import CallBackLocators, FieldSelector
from pages.jones.call_back.call_back_types import CallBackForm
from utilities.base.css_colors import RGBA, Background

_LABEL_STYLE_TIMEOUT_MS: int = 3_000
_LABEL_STYLE_POLL_MS: int = 100


class CallBackPage(BasePage):
    """Fills the lead form, switches company size and submits it."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.loc = CallBackLocators()

    # ---------- locators ---------- #

    def field(self, selector: FieldSelector) -> Locator:
        return self.by_id_or_label(selector.element_id, selector.label)

    @property
    def form(self) -> Locator:
        return self.page.locator(self.loc.FORM_CSS)

    @property
    def submit_button(self) -> Locator:
        return self.form.get_by_role("button", name=self.loc.SUBMIT_BUTTON_TEXT)

    def label(self, selector: FieldSelector) -> Locator:
        return self.form.locator(self.loc.LABEL_CSS_TEMPLATE.format(element_id=selector.element_id))

    def label_background(self, selector: FieldSelector) -> Background:
        """Computed background of the field's <label> (color + image)."""
        return Background.from_computed(
            self.label(selector).evaluate(
                "el => { const s = getComputedStyle(el);"
                " return [s.backgroundColor, s.backgroundImage]; }"
            )
        )

    def wait_for_label_background(
        self,
        selector: FieldSelector,
        rgba: RGBA,
        *,
        timeout_ms: int = _LABEL_STYLE_TIMEOUT_MS,
    ) -> Background:
        """Poll until the label paints ``rgba`` (tolerates CSS transitions); return the last read."""
        deadline: float = time.monotonic() + timeout_ms / 1000
        background = self.label_background(selector)
        while background.color != rgba and time.monotonic() < deadline:
            self.page.wait_for_timeout(_LABEL_STYLE_POLL_MS)
            background = self.label_background(selector)
        return background

    def validation_messages(self) -> dict[str, str]:
        """Browser validation message per invalid control id."""
        return dict(
            self.form.evaluate(
                "f => [...f.elements].filter(el => el.willValidate && !el.validity.valid)"
                ".map(el => [el.id, el.validationMessage])"
            )
        )

    def invalid_field_ids(self) -> list[str]:
        """Ids of controls failing native HTML5 validation (required / type=email / type=url)."""
        return list(
            self.form.evaluate(
                "f => [...f.elements].filter(el => el.willValidate && !el.validity.valid)"
                ".map(el => el.id)"
            )
        )

    # ---------- actions ---------- #

    @allure.step("Open the call-back form")
    def open(self, url: str) -> None:
        self.goto(url)
        self.submit_button.wait_for(state="visible")

    @allure.step("Fill contact details")
    def fill_contact_details(self, form: CallBackForm) -> None:
        self.fill(self.field(self.loc.NAME), form.name, "Name")
        self.fill(self.field(self.loc.EMAIL), form.email, "Email")
        self.fill(self.field(self.loc.PHONE), form.phone, "Phone")
        self.fill(self.field(self.loc.COMPANY), form.company, "Company")
        self.fill(self.field(self.loc.WEBSITE), form.website, "Website")

    def selected_employees(self) -> str:
        return self.selected_option_text(self.field(self.loc.EMPLOYEES))

    @allure.step("Change Number of Employees to {employees!r}")
    def select_employees(self, employees: str) -> None:
        self.select(self.field(self.loc.EMPLOYEES), employees, "Number of Employees")

    def focus_field(self, selector: FieldSelector) -> None:
        with allure.step(f"Click into the {selector.label!r} field"):
            self.click(self.field(selector), selector.label)

    @allure.step("Click 'Request a call back'")
    def submit(self) -> None:
        self.click(self.submit_button, self.loc.SUBMIT_BUTTON_TEXT)
