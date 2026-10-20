"""DDT: empty and invalid input from ``resources/test_data/<env>/invalid_leads.csv``.

Each row must be blocked on the form, with native validation flagging exactly the
listed inputs. Rows with a ``known_issue`` document gaps the site does not catch
today and run as strict xfail.
"""

from __future__ import annotations

import allure
import pytest

from fixtures.call_back import lead_to_form, make_run_id
from pages.jones.call_back.call_back_page import CallBackPage
from pages.jones.call_back.call_back_types import SubmitOutcome
from utilities.base.envs import EnvConfig
from utilities.base.lead_csv_schema import LeadRow
from utilities.base.verifications import Verifications
from workflows.call_back_workflow import THANK_YOU_LOG_MESSAGE, CallBackWorkflow


@allure.feature("Lead capture")
@allure.story("Invalid submissions (CSV)")
@pytest.mark.call_back
def test_invalid_lead_is_blocked(
    invalid_lead: LeadRow,
    env_config: EnvConfig,
    call_back_page: CallBackPage,
    call_back_workflow: CallBackWorkflow,
    console_messages: list[str],
    verify: Verifications,
) -> None:
    allure.dynamic.title(f"{invalid_lead.id}: {invalid_lead.description}")
    allure.dynamic.description(
        f"Data: {env_config.test_data_dir.name}/invalid_leads.csv\n"
        f"Expected invalid: {sorted(invalid_lead.invalid_fields)}\n"
        f"Known issue: {invalid_lead.known_issue or '-'}"
    )

    run_id = make_run_id(invalid_lead.id)
    form = lead_to_form(invalid_lead, run_id=run_id)

    result = call_back_workflow.run(form, screenshot_name=run_id, expect_thank_you=False)

    verify.equals(result.outcome, SubmitOutcome.STAYS_ON_FORM, what="Outcome after submit")
    verify.equals(result.url, env_config.home_url, what="URL after a blocked submit")
    verify.equals(
        frozenset(result.invalid_fields),
        invalid_lead.invalid_fields,
        what="Inputs flagged by validation",
    )
    messages = call_back_page.validation_messages()
    for field_id in sorted(invalid_lead.invalid_fields):
        verify.is_true(
            bool(messages.get(field_id)),
            what=f"#{field_id} shows a validation message ({messages.get(field_id)!r})",
        )
    verify.is_false(
        any(THANK_YOU_LOG_MESSAGE in line for line in console_messages),
        what="No thank-you console.log on a blocked submit",
    )
