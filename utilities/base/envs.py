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

DEFAULT_MOCK_PORT: Final[int] = 8765


class Env(str, Enum):
    LOCAL = "local"
    PROD = "prod"


def _mock_port() -> int:
    return int(os.getenv("JONES_MOCK_PORT") or DEFAULT_MOCK_PORT)


def _default_base_url(env: Env) -> str:
    if env == Env.LOCAL:
        return f"http://127.0.0.1:{_mock_port()}"
    return "https://test.netlify.app"


@dataclass(frozen=True)
class EnvConfig:
    """Resolved configuration for a single test run."""

    env: Env
    base_url: str
    browser_channel: str | None
    mock_port: int
    repo_root: Path

    @property
    def home_url(self) -> str:
        return f"{self.base_url}/"

    @property
    def serves_mock_site(self) -> bool:
        """True when the suite should start the bundled mock site itself."""
        return self.env == Env.LOCAL and not os.getenv("JONES_BASE_URL")

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

    base_url = os.getenv("JONES_BASE_URL") or _default_base_url(env)
    return EnvConfig(
        env=env,
        base_url=base_url.rstrip("/"),
        browser_channel=os.getenv("JONES_BROWSER_CHANNEL") or None,
        mock_port=_mock_port(),
        repo_root=_REPO_ROOT,
    )
