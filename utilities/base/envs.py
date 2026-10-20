"""Environment resolution.

Single source of truth for the site URL and tunables. Reads values from process
env (populated by `.env` via python-dotenv) and falls back to a static per-env map.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env", override=False)


class Env(str, Enum):
    PROD = "prod"


_BASE_URLS: Final[dict[Env, str]] = {
    Env.PROD: "https://test.netlify.app",
}


@dataclass(frozen=True)
class EnvConfig:
    """Resolved configuration for a single test run."""

    env: Env
    base_url: str
    browser_channel: str | None
    repo_root: Path

    @property
    def home_url(self) -> str:
        return f"{self.base_url}/"

    @property
    def test_data_dir(self) -> Path:
        """Per-env CSV data: ``resources/test_data/<env>/``."""
        return self.repo_root / "resources" / "test_data" / self.env.value

    @property
    def reports_dir(self) -> Path:
        return self.repo_root / "reports"


def resolve(env_name: str | None = None) -> EnvConfig:
    """Build an EnvConfig from CLI arg + process environment."""
    name = (env_name or os.getenv("ENV") or Env.PROD.value).lower()
    try:
        env = Env(name)
    except ValueError as exc:
        valid = ", ".join(e.value for e in Env)
        raise ValueError(f"Unknown env '{name}'. Valid options: {valid}") from exc

    base_url = os.getenv("JONES_BASE_URL") or _BASE_URLS[env]
    return EnvConfig(
        env=env,
        base_url=base_url.rstrip("/"),
        browser_channel=os.getenv("JONES_BROWSER_CHANNEL") or None,
        repo_root=_REPO_ROOT,
    )
