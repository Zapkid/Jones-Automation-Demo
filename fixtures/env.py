"""Env fixtures — resolve the EnvConfig once per session, start the mock site for local."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from utilities.base.envs import EnvConfig, resolve
from utilities.server.mock_site import MockSiteServer


@pytest.fixture(scope="session")
def env_config(request: pytest.FixtureRequest) -> EnvConfig:
    return resolve(request.config.getoption("--env"))


@pytest.fixture(scope="session", autouse=True)
def mock_site(env_config: EnvConfig) -> Iterator[MockSiteServer | None]:
    """Serve ``resources/mock_site`` when running ``--env=local`` without a URL override.

    Under xdist several workers race for the same port; the first one wins and
    the others reuse its server, which lives until that worker exits.
    """
    if not env_config.serves_mock_site:
        yield None
        return
    try:
        server = MockSiteServer(env_config.mock_port).start()
    except OSError:
        yield None
        return
    try:
        yield server
    finally:
        server.stop()
