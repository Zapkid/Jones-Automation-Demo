"""Allure helpers — screenshots, failure artifacts and report shell-outs."""

from __future__ import annotations

import subprocess
from pathlib import Path

import allure
from playwright.sync_api import Page


def attach_screenshot(page: Page, name: str, screenshots_dir: Path) -> Path:
    """Save a full-page screenshot to disk and attach it to the current Allure step."""
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    path = screenshots_dir / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    allure.attach.file(str(path), name=name, attachment_type=allure.attachment_type.PNG)
    return path


def attach_console_log(lines: list[str], name: str = "browser-console") -> None:
    """Attach captured browser console output as a text attachment."""
    allure.attach(
        "\n".join(lines) or "(no console output)",
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )


def attach_failure_artifacts(page: Page, stem: str, reports_dir: Path) -> None:
    """Attach screenshot, URL, and DOM to the current Allure step.

    Safe to call from a pytest hook even when the page has already navigated
    away — every individual attachment is wrapped so one failure doesn't
    suppress the others.
    """
    try:
        attach_screenshot(page, f"{stem}-failure", reports_dir / "screenshots")
    except Exception as exc:  # noqa: BLE001
        allure.attach(f"screenshot failed: {exc}", name="screenshot-error")

    try:
        allure.attach(page.url, name="page-url", attachment_type=allure.attachment_type.TEXT)
    except Exception:
        pass

    try:
        allure.attach(
            page.content(), name=f"{stem}-dom", attachment_type=allure.attachment_type.HTML
        )
    except Exception:
        pass


def generate_report(results_dir: Path, output_dir: Path) -> None:
    """Shell out to the Allure CLI to produce the static HTML report."""
    subprocess.check_call(
        ["allure", "generate", str(results_dir), "-o", str(output_dir), "--clean"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
