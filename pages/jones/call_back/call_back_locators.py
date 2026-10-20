"""Selectors for the "Request a call back" form.

Each field is resolved by accessible label first, then placeholder, then the
``name`` attribute — so the page object survives small markup changes on the
real site without touching tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldSelector:
    label: str
    name_attr: str


@dataclass(frozen=True)
class CallBackLocators:
    NAME: FieldSelector = FieldSelector(label="Name", name_attr="name")
    EMAIL: FieldSelector = FieldSelector(label="Email", name_attr="email")
    PHONE: FieldSelector = FieldSelector(label="Phone", name_attr="phone")
    COMPANY: FieldSelector = FieldSelector(label="Company", name_attr="company")
    WEBSITE: FieldSelector = FieldSelector(label="Website", name_attr="website")
    EMPLOYEES: FieldSelector = FieldSelector(label="Number of Employees", name_attr="employees")

    SUBMIT_BUTTON_TEXT: str = "Request a call back"
