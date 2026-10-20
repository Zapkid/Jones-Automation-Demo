"""Typed models for the "Request a call back" form."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Final

DEFAULT_EMPLOYEES: Final[str] = "1-10"


class SubmitOutcome(str, Enum):
    THANK_YOU = "thank_you"
    STAYS_ON_FORM = "stays_on_form"


@dataclass(frozen=True)
class CallBackForm:
    """Values typed into the lead form. ``employees`` None keeps the page default."""

    name: str
    email: str
    phone: str
    company: str
    website: str
    employees: str | None = None


@dataclass(frozen=True)
class SubmitResult:
    outcome: SubmitOutcome
    url: str
    heading: str | None
    screenshot_before_submit: str
    employees_selected: str
    # Native HTML5 validation failures left on the form when it did not submit.
    invalid_fields: tuple[str, ...] = field(default=())
    # Query string the GET form carried to the thank-you page (the form has no method).
    submitted: dict[str, str] = field(default_factory=dict)
