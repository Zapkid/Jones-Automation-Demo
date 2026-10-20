"""Page object for the landing page "Request a call back" lead form."""

from __future__ import annotations

import allure
from playwright.sync_api import Locator, Page

from pages.base.base_page import BasePage
from pages.jones.call_back.call_back_locators import CallBackLocators, FieldSelector
from pages.jones.call_back.call_back_types import CallBackForm


class CallBackPage(BasePage):
    """Fills the lead form, switches company size and submits it."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.loc = CallBackLocators()

    # ---------- locators ---------- #

    def field(self, selector: FieldSelector) -> Locator:
        return self.by_label_placeholder_or_name(selector.label, selector.name_attr)

    @property
    def submit_button(self) -> Locator:
        return (
            self.page.get_by_role("button", name=self.loc.SUBMIT_BUTTON_TEXT, exact=False)
            .or_(self.page.locator(f"input[type=submit][value*='{self.loc.SUBMIT_BUTTON_TEXT}' i]"))
            .first
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

    @allure.step("Click 'Request a call back'")
    def submit(self) -> None:
        self.click(self.submit_button, self.loc.SUBMIT_BUTTON_TEXT)
