"""End-to-end "Request a call back" business flow.

Orchestrates the call-back and thank-you page objects so tests read as a
single intention: fill → (optionally) resize company → screenshot → submit →
detect the thank-you page → console.log.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import allure

from pages.jones.call_back.call_back_page import CallBackPage
from pages.jones.call_back.call_back_types import CallBackForm, SubmitOutcome, SubmitResult
from pages.jones.thank_you.thank_you_page import ThankYouPage
from utilities.allure.allure import attach_screenshot
from utilities.base.envs import EnvConfig

THANK_YOU_LOG_MESSAGE: str = "Reached the thank you page"
_NEGATIVE_WAIT_MS: int = 3_000


@dataclass
class CallBackWorkflow:
    env_config: EnvConfig
    call_back: CallBackPage
    thank_you: ThankYouPage

    def run(
        self,
        form: CallBackForm,
        *,
        screenshot_name: str,
        expect_thank_you: bool = True,
    ) -> SubmitResult:
        self.call_back.open(self.env_config.home_url)
        self.call_back.fill_contact_details(form)
        if form.employees is not None:
            self.call_back.select_employees(form.employees)

        employees_selected = self.call_back.selected_employees()
        screenshot = self._screenshot_before_submit(screenshot_name)
        self.call_back.submit()

        reached: bool = self.thank_you.wait_until_reached(
            **({} if expect_thank_you else {"timeout_ms": _NEGATIVE_WAIT_MS})
        )
        url: str = self.call_back.page.url
        if not reached:
            return SubmitResult(
                outcome=SubmitOutcome.STAYS_ON_FORM,
                url=url,
                heading=None,
                screenshot_before_submit=str(screenshot),
                employees_selected=employees_selected,
                invalid_fields=tuple(self.call_back.invalid_field_ids()),
            )

        self.thank_you.log_arrival(f"{THANK_YOU_LOG_MESSAGE}: {url}")
        return SubmitResult(
            outcome=SubmitOutcome.THANK_YOU,
            url=url,
            heading=self.thank_you.heading,
            screenshot_before_submit=str(screenshot),
            employees_selected=employees_selected,
            submitted=dict(parse_qsl(urlsplit(url).query)),
        )

    @allure.step("Screenshot the page before clicking 'Request a call back'")
    def _screenshot_before_submit(self, name: str) -> Path:
        return attach_screenshot(
            self.call_back.page,
            f"before_submit_{name}",
            self.env_config.reports_dir / "screenshots",
        )
