"""Fixtures specific to the "Request a call back" form.

Split out of tests/conftest.py so other suites (e.g. a future pricing-page
form) can reuse the page objects and case helpers.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Final

import pytest
from playwright.sync_api import Page

from pages.jones.call_back.call_back_page import CallBackPage
from pages.jones.call_back.call_back_types import CallBackForm
from pages.jones.thank_you.thank_you_page import ThankYouPage
from utilities.base.call_back_case_schema import (
    CallBackCaseValidationError,
    validate_call_back_cases_document,
)
from utilities.base.envs import EnvConfig
from utilities.base.json_data import load_json_file
from utilities.base.lead_csv_schema import LeadRow, load_invalid_leads, load_valid_leads
from utilities.base.verifications import Verifications
from workflows.call_back_workflow import CallBackWorkflow

CALL_BACK_CASES_FILE: Final[Path] = (
    Path(__file__).resolve().parents[1] / "resources" / "test_data" / "call_back_cases.jsonc"
)
VALID_LEADS_CSV: Final[str] = "valid_leads.csv"
INVALID_LEADS_CSV: Final[str] = "invalid_leads.csv"
_RUN_ID_TOKEN: Final[str] = "{run_id}"


# ---------- page object fixtures ---------- #


@pytest.fixture
def call_back_page(page: Page) -> CallBackPage:
    return CallBackPage(page)


@pytest.fixture
def thank_you_page(page: Page) -> ThankYouPage:
    return ThankYouPage(page)


@pytest.fixture
def call_back_workflow(
    env_config: EnvConfig,
    call_back_page: CallBackPage,
    thank_you_page: ThankYouPage,
) -> CallBackWorkflow:
    return CallBackWorkflow(
        env_config=env_config,
        call_back=call_back_page,
        thank_you=thank_you_page,
    )


@pytest.fixture
def verify() -> Verifications:
    return Verifications()


# ---------- data-driven cases ---------- #


def load_call_back_cases(path: Path = CALL_BACK_CASES_FILE) -> list[dict[str, Any]]:
    try:
        return validate_call_back_cases_document(load_json_file(path))
    except CallBackCaseValidationError as exc:
        raise CallBackCaseValidationError(f"{path}: {exc}") from exc


def make_run_id(case_id: str) -> str:
    """Unique, sortable id so each submitted lead can be traced back to its run."""
    return f"{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}-{case_id.lower()}"


def case_to_form(case: dict[str, Any], *, run_id: str) -> CallBackForm:
    form: dict[str, str] = {
        key: value.replace(_RUN_ID_TOKEN, run_id) for key, value in case["form"].items()
    }
    return CallBackForm(
        name=form["name"],
        email=form["email"],
        phone=form["phone"],
        company=form["company"],
        website=form["website"],
        employees=form.get("employees"),
    )


def load_env_valid_leads(env_config: EnvConfig) -> list[LeadRow]:
    return load_valid_leads(env_config.test_data_dir / VALID_LEADS_CSV)


def load_env_invalid_leads(env_config: EnvConfig) -> list[LeadRow]:
    return load_invalid_leads(env_config.test_data_dir / INVALID_LEADS_CSV)


def lead_to_form(lead: LeadRow, *, run_id: str) -> CallBackForm:
    """Expand ``{run_id}`` in every text value of a CSV row."""
    form = lead.form
    return CallBackForm(
        name=form.name.replace(_RUN_ID_TOKEN, run_id),
        email=form.email.replace(_RUN_ID_TOKEN, run_id),
        phone=form.phone.replace(_RUN_ID_TOKEN, run_id),
        company=form.company.replace(_RUN_ID_TOKEN, run_id),
        website=form.website.replace(_RUN_ID_TOKEN, run_id),
        employees=form.employees,
    )
