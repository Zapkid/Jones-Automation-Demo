"""Data-driven end-to-end tests for the "Request a call back" lead form.

Each case in `resources/test_data/call_back_cases.jsonc` becomes one
parametrized test invocation. The flow:

  1. Opens the landing page.
  2. Types Name, Email, Phone, Company and Website.
  3. (Bonus) Changes Number of Employees from 1-10 to 51-500.
  4. Screenshots the page before clicking "Request a call back".
  5. Clicks "Request a call back".
  6. Writes to console.log when the thank-you page is reached.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import allure
import pytest

from fixtures.call_back import case_to_form, make_run_id
from pages.jones.call_back.call_back_page import CallBackPage
from pages.jones.call_back.call_back_types import DEFAULT_EMPLOYEES, SubmitOutcome
from utilities.base.envs import EnvConfig
from utilities.base.verifications import Verifications
from workflows.call_back_workflow import THANK_YOU_LOG_MESSAGE, CallBackWorkflow


@allure.feature("Lead capture")
@allure.story("Request a call back")
@pytest.mark.call_back
def test_request_call_back(
    case: dict[str, Any],
    env_config: EnvConfig,
    call_back_page: CallBackPage,
    call_back_workflow: CallBackWorkflow,
    console_messages: list[str],
    verify: Verifications,
) -> None:
    allure.dynamic.title(case["description"])
    allure.dynamic.description(
        f"Case id: {case['id']}\nEnv: {env_config.env.value}\nBase URL: {env_config.base_url}"
    )

    run_id = make_run_id(str(case["id"]))
    form = case_to_form(case, run_id=run_id)
    expected = SubmitOutcome(case["expected"]["outcome"])

    if form.employees is not None:
        # Bonus precondition: the page must start on the default bucket.
        call_back_page.open(env_config.home_url)
        verify.equals(
            call_back_page.selected_employees(),
            DEFAULT_EMPLOYEES,
            what="Default Number of Employees",
        )

    result = call_back_workflow.run(
        form,
        screenshot_name=run_id,
        expect_thank_you=expected == SubmitOutcome.THANK_YOU,
    )

    verify.is_true(
        Path(result.screenshot_before_submit).is_file(),
        what="Screenshot was taken before clicking 'Request a call back'",
    )
    verify.equals(result.outcome, expected, what="Outcome after submit")

    if expected == SubmitOutcome.THANK_YOU:
        verify.is_true(
            any(THANK_YOU_LOG_MESSAGE in line for line in console_messages),
            what="Thank-you arrival was written to console.log",
        )
    else:
        verify.is_false(
            any(THANK_YOU_LOG_MESSAGE in line for line in console_messages),
            what="No thank-you console.log on a rejected submit",
        )
