"""Parse computed CSS colors so style checks don't depend on rgb()/rgba() spelling."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

RGBA = tuple[int, int, int, float]

TRANSPARENT: Final[RGBA] = (0, 0, 0, 0.0)
_RGB_RE: Final[re.Pattern[str]] = re.compile(
    r"rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)"
)


def parse_css_color(value: str) -> RGBA:
    """``rgb(122, 184, 147)`` / ``rgba(122,184,147,1)`` / ``transparent`` -> (r, g, b, a)."""
    text = value.strip().lower()
    if text == "transparent":
        return TRANSPARENT
    match = _RGB_RE.fullmatch(text)
    if match is None:
        raise ValueError(f"Unsupported CSS color: {value!r}")
    red, green, blue, alpha = match.groups()
    if alpha is None:
        alpha_value = 1.0
    elif alpha.endswith("%"):
        alpha_value = float(alpha[:-1]) / 100
    else:
        alpha_value = float(alpha)
    return (int(red), int(green), int(blue), round(alpha_value, 3))


@dataclass(frozen=True)
class Background:
    """Computed label background: parsed color plus the raw background-image."""

    color: RGBA
    image: str

    @classmethod
    def from_computed(cls: type[Background], computed: list[str]) -> Background:
        color, image = computed
        return cls(color=parse_css_color(color), image=image)

    @property
    def is_none(self) -> bool:
        """CSS `background: none` computes to a fully transparent color and no image."""
        return self.color[3] == 0 and self.image == "none"
