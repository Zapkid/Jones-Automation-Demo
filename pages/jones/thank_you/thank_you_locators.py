"""Selectors / signals for the post-submit thank-you page."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThankYouLocators:
    URL_PATTERN: str = r"thank"
    HEADING_PATTERN: str = r"thank\s*you"

    HEADING_TEXT: str = "Thank You!"
    SUBHEADING_TEXT: str = "You'll hear from us soon."
    BACK_HOME_LINK_TEXT: str = "Back to Home"
