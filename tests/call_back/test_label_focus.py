"""Focus styling: clicking into an input paints its <label> rgba(122,184,147,1).

Before the click every label's background is ``none`` (transparent, no image);
after it, only the focused field's label turns green.
"""

from __future__ import annotations

import allure
import pytest

from pages.jones.call_back.call_back_locators import CallBackLocators, FieldSelector
from pages.jones.call_back.call_back_page import CallBackPage
from utilities.base.envs import EnvConfig
from utilities.base.verifications import Verifications

_LOC = CallBackLocators()


@allure.feature("Lead capture")
@allure.story("Label focus styling")
@pytest.mark.call_back
@pytest.mark.regression
@pytest.mark.parametrize(
    "field", _LOC.TEXT_FIELDS, ids=[selector.element_id for selector in _LOC.TEXT_FIELDS]
)
def test_label_background_on_focus(
    field: FieldSelector,
    env_config: EnvConfig,
    call_back_page: CallBackPage,
    verify: Verifications,
) -> None:
    allure.dynamic.title(f"Clicking {field.label!r} paints its label green")
    call_back_page.open(env_config.home_url)

    for selector in _LOC.TEXT_FIELDS:
        before = call_back_page.label_background(selector)
        verify.is_true(
            before.is_none,
            what=f"{selector.label!r} label background is none before focus ({before})",
        )

    call_back_page.focus_field(field)

    after = call_back_page.wait_for_label_background(field, _LOC.LABEL_FOCUS_BACKGROUND)
    verify.equals(
        after.color,
        _LOC.LABEL_FOCUS_BACKGROUND,
        what=f"{field.label!r} label background-color after focus (rgba)",
    )
    for other in _LOC.TEXT_FIELDS:
        if other == field:
            continue
        background = call_back_page.label_background(other)
        verify.is_true(
            background.is_none,
            what=f"{other.label!r} label stays unpainted while {field.label!r} is focused",
        )
