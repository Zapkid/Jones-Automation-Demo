"""Tiny static server for ``resources/mock_site`` — a stand-in for the real site.

Used by ``--env=local`` so the suite (and CI) can run end-to-end without
network access to the site under test. Run standalone with ``make mock-site``.
"""

from __future__ import annotations

import argparse
import logging
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Final

from utilities.base.envs import DEFAULT_MOCK_PORT

MOCK_SITE_DIR: Final[Path] = Path(__file__).resolve().parents[2] / "resources" / "mock_site"
logger = logging.getLogger(__name__)


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        logger.debug("mock-site: " + format, *args)


class MockSiteServer:
    """Serve the mock site on a background thread for the duration of a session."""

    def __init__(self, port: int, host: str = "127.0.0.1") -> None:
        handler = partial(_QuietHandler, directory=str(MOCK_SITE_DIR))
        self._httpd = ThreadingHTTPServer((host, port), handler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        host, port = self._httpd.server_address[:2]
        return f"http://{host}:{port}"

    def start(self) -> MockSiteServer:
        self._thread.start()
        logger.info("Mock site serving %s at %s", MOCK_SITE_DIR, self.url)
        return self

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the bundled mock site.")
    parser.add_argument("--port", type=int, default=DEFAULT_MOCK_PORT)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    server = MockSiteServer(args.port).start()
    try:
        server._thread.join()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
