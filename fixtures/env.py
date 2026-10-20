"""Env fixture — resolves the EnvConfig once per session, honors `--env`."""

from __future__ import annotations

import pytest

from utilities.base.envs import EnvConfig, resolve


@pytest.fixture(scope="session")
def env_config(request: pytest.FixtureRequest) -> EnvConfig:
    return resolve(request.config.getoption("--env"))
