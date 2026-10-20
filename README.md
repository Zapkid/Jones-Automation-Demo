# jones-aqa

Playwright + pytest + Allure automation for the **"Request a call back"** lead form.
Page Object Model, typed Python, data-driven cases, and an offline mock site so the suite
runs anywhere, including CI.

## Resources

| | |
| --- | --- |
| **Billing widget review (UI mock-up Q&A)** | [docs/billing-widget-review.md](docs/billing-widget-review.md) |
| **Architecture** | [docs/architecture.md](docs/architecture.md) |

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

## Layout

```txt
.
├── docs/                # Architecture, billing-widget review, exercise images
├── fixtures/            # pytest fixtures (env + mock site, browser, call-back)
├── pages/               # Page Object Model
│   ├── base/
│   └── jones/           # call_back, thank_you
├── reports/             # Allure, traces, screenshots (gitignored)
├── resources/
│   ├── mock_site/       # Offline stand-in for the landing + thank-you pages
│   └── test_data/       # call_back_cases.jsonc
├── tests/               # Test suites only
├── utilities/           # env, driver, Allure, JSONC + schema, mock server
└── workflows/           # Multi-page business flows
```

## Test cases

| Id | Markers | Flow | Expected |
| --- | --- | --- | --- |
| CB1 | smoke | Fill all fields, keep default size, screenshot, submit | Thank-you page + console.log |
| CB2 | smoke | Same, plus size 1-10 → 51-500 (bonus) | Thank-you page + console.log |
| CB3 | regression · local only | Invalid email | Stays on form, no console.log |

To add a case, add an entry to `resources/test_data/call_back_cases.jsonc`. It's schema-checked at
collection. `{run_id}` in any value expands to a unique, timestamped id per run.

## Make targets

| Target | Description |
| --- | --- |
| `make install` | Editable install with dev deps |
| `make browsers` | `playwright install --with-deps chromium` |
| `make test` | Full suite |
| `make test-smoke` | `-m smoke` |
| `make test-regression` | `-m regression` |
| `make test-call-back` | `-m call_back` |
| `make mock-site` | Serve the mock site on :8765 for manual poking |
| `make allure-serve` | Open Allure report from last run |
| `make lint` / `make format` | black + isort + flake8 |

Make variables: `ENV` (default `prod`), `HEADED=1`, `SLOWMO=250`, `WORKERS=4`.

## pytest CLI

```bash
pytest \
  --env=local \          # local | prod
  --browser=chromium \   # chromium | firefox | webkit
  --headed \             # visible browser
  --slowmo=250 \         # ms delay between actions
  --keep-traces \        # keep Playwright traces for passing tests too
  -n=4                   # parallel workers (pytest-xdist)
```

## Artifacts

- Pre-submit screenshot: `reports/screenshots/before_submit_{run_id}.png` (every run)
- On failure: screenshot, URL and DOM in Allure, plus a trace in `reports/traces/{case}_{ts}.zip`
- Browser console log: attached to every test in Allure
