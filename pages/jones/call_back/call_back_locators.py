"""Selectors for the "Request a call back" form on https://test.netlify.app/.

Every input has a stable ``id``, so that is the primary hook. The accessible
label is OR-ed in as a fallback in case the ids change. Placeholders are not
used because "Company name" would also match a loose "Name" lookup.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldSelector:
    element_id: str
    label: str


@dataclass(frozen=True)
class CallBackLocators:
    NAME: FieldSelector = FieldSelector(element_id="name", label="Name *")
    EMAIL: FieldSelector = FieldSelector(element_id="email", label="Email *")
    PHONE: FieldSelector = FieldSelector(element_id="phone", label="Phone *")
    COMPANY: FieldSelector = FieldSelector(element_id="company", label="Company")
    WEBSITE: FieldSelector = FieldSelector(element_id="website", label="Website")
    EMPLOYEES: FieldSelector = FieldSelector(element_id="employees", label="Number of Employees")

    FORM_CSS: str = "form[action*='thank-you']"
    SUBMIT_BUTTON_TEXT: str = "Request a call back"
