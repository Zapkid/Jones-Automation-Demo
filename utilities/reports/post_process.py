"""Optional Allure post-processing hooks (environment.properties, categories.json)."""

from __future__ import annotations

import json
from pathlib import Path


def write_environment_properties(results_dir: Path, env_name: str, base_url: str) -> None:
    """Drop the Allure `environment.properties` file so the report shows env metadata."""
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "environment.properties").write_text(
        f"env={env_name}\nbase_url={base_url}\n",
        encoding="utf-8",
    )


def write_categories(results_dir: Path) -> None:
    """Define Allure failure categories so flaky vs. real failures are grouped."""
    results_dir.mkdir(parents=True, exist_ok=True)
    categories = [
        {
            "name": "Product defects",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*AssertionError.*",
        },
        {
            "name": "Test infrastructure",
            "matchedStatuses": ["broken"],
        },
        {
            "name": "Flaky tests",
            "matchedStatuses": ["passed"],
            "messageRegex": ".*reran.*",
        },
    ]
    (results_dir / "categories.json").write_text(json.dumps(categories, indent=2))
