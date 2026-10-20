"""DDT: valid lead combinations from ``resources/test_data/<env>/valid_leads.csv``.

Every row must reach the thank-you page and the GET query string must carry back
exactly what was typed, so the test proves each value was actually submitted.
"""

from __future__ import annotations

import allure
import pytest

from fixtures.call_back import lead_to_form, make_run_id
from pages.jones.call_back.call_back_types import SubmitOutcome
from pages.jones.thank_you.thank_you_locators import ThankYouLocators
from pages.jones.thank_you.thank_you_page import ThankYouPage
from utilities.base.envs import EnvConfig
from utilities.base.lead_csv_schema import LeadRow
from utilities.base.verifications import Verifications
from workflows.call_back_workflow import THANK_YOU_LOG_MESSAGE, CallBackWorkflow


@allure.feature("Lead capture")
@allure.story("Valid submissions (CSV)")
@pytest.mark.call_back
def test_valid_lead_reaches_thank_you(
    valid_lead: LeadRow,
    env_config: EnvConfig,
    call_back_workflow: CallBackWorkflow,
    thank_you_page: ThankYouPage,
    console_messages: list[str],
    verify: Verifications,
) -> None:
    allure.dynamic.title(f"{valid_lead.id}: {valid_lead.description}")
    allure.dynamic.description(
        f"Data: {env_config.test_data_dir.name}/valid_leads.csv\nBase URL: {env_config.base_url}"
    )

    run_id = make_run_id(valid_lead.id)
    form = lead_to_form(valid_lead, run_id=run_id)

    result = call_back_workflow.run(form, screenshot_name=run_id)

    verify.equals(result.outcome, SubmitOutcome.THANK_YOU, what="Outcome after submit")
    thank_you = ThankYouLocators()
    verify.equals(result.heading, thank_you.HEADING_TEXT, what="Thank-you heading")
    verify.equals(thank_you_page.subheading, thank_you.SUBHEADING_TEXT, what="Thank-you subheading")
    verify.equals(thank_you_page.back_home_href, "/", what="'Back to Home' link target")
    verify.is_true(
        any(THANK_YOU_LOG_MESSAGE in line for line in console_messages),
        what="Thank-you arrival was written to console.log",
    )

    expected_submission: dict[str, str] = {
        "name": form.name,
        "email": form.email,
        "phone": form.phone,
        "company": form.company,
        "website": form.website,
        "number_of_employees": form.employees or "",
    }
    for key, value in expected_submission.items():
        verify.equals(result.submitted.get(key), value, what=f"Submitted {key}")
