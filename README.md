# jones-aqa

Playwright + pytest + Allure automation for the **"Request a call back"** lead form on
`https://test.netlify.app/`, plus a QA review of a billing widget mock-up.

## Docs

| Doc | What's in it |
| --- | --- |
| [Billing widget review](docs/billing-widget-review.md) | UI mock-up Q&A: problems found, sample test cases, solution for the most severe bug |
| [Test cases](docs/test-cases.md) | What each suite checks, the per-env CSV data, known issues pinned as xfail |
| [Live site findings](docs/live-site-findings.md) | Bugs and risks found on the real page while automating it |
| [Running the suite](docs/running.md) | Make targets, pytest options, screenshots/traces/Allure artifacts |
| [Architecture](docs/architecture.md) | Repo layout, layers, environments, reporting |

## The exercise

![Automation exercise](docs/assets/automation-exercise.jpg)

| Requirement | Where |
| --- | --- |
| Type Name, Email, Phone, Company, Website | `CallBackPage.fill_contact_details` |
| Screenshot before clicking "Request a call back" | `CallBackWorkflow._screenshot_before_submit` → `reports/screenshots/before_submit_*.png` + Allure attachment |
| **Bonus:** Number of Employees 1-10 → 51-500 | Case `CB2`: checks the default is `1-10`, then `CallBackPage.select_employees("51-500")` |
| Click "Request a call back" | `CallBackPage.submit` |
| console.log on the thank-you page | `ThankYouPage.log_arrival`: browser `console.log` + Python log, asserted by the test |

## Quick start

```bash
# 1. Python environment
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Playwright browser
playwright install --with-deps chromium

# 3. Run against the real site (default env=prod)
make test

# …or fully offline against the bundled mock site
make test ENV=local

# 4. Open the Allure report
make allure-serve
```

Optional: `cp .env.example .env` to change defaults (`ENV`, `JONES_BASE_URL`, mock port).
