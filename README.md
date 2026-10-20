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

## My approach to automation and QA

These are the principles behind the project. The next section shows where each one is applied.

1. **A test is evidence, not a script.** It should check an outcome someone cares about (what
   was submitted, what the user saw), not just that steps ran without an exception.
2. **Automate by risk.** The flows that lose revenue or leads come first, and so do the
   regressions people actually make. Tests against live systems should have small, traceable
   side effects.
3. **Keep data separate from logic.** Cases live in data files with a schema, so adding a
   scenario is a data change, and a bad row fails fast with a clear message.
4. **Deterministic and isolated.** Every test gets a fresh browser context. Waits are on
   conditions, not fixed sleeps. Tests can run in parallel.
5. **A failure should explain itself.** Every check is a named step. A failure attaches a
   screenshot, URL, page HTML, browser console and a trace. Allure groups failures into product
   defects and test infrastructure.
6. **Track known bugs in the suite; never hide them.** A test is never skipped or deleted to get
   green. A known defect becomes a strict expected failure, so the suite says when it's fixed.
7. **Locators follow the page's contract, not its layout.** Ids and accessible labels come first.
   Layout-based selectors and text that can match more than one element are avoided.
8. **Layers with one job each.** Tests state intent, workflows run business flows, page objects
   own selectors, and a `Verifications` layer does every assertion.
9. **Fast feedback in CI.** Lint and the full suite run on every PR, with a secret scan alongside.
   Artifacts are uploaded whether the run passes or fails.
10. **Automation is one tool among several.** Reading the markup and exploring by hand find
    things a script won't. Those findings are reported with severity, impact and a proposed
    fix, because quality is a product conversation, not a pass/fail count.

## Beyond the brief

The brief asks for a script that fills the form and clicks a button. These are the decisions
made on top of that, and why.

**Prove it, don't just do it**
- **console.log is checked, not just written.** The test reads the browser's console events and
  fails if the thank-you message never appears there.
- **The bonus is proven end to end.** The test checks the dropdown starts at `1-10`, changes it,
  and then reads `number_of_employees=51-500` back from the thank-you URL. The form submits by GET,
  so the URL shows what was actually sent, not what the page displayed.
- **The focus-colour test was checked against a wrong colour.** Changing the label colour by a
  few units made it fail. Colours are compared as numbers, so `rgb()` and `rgba()` spellings
  both match, and the test waits out CSS transitions.

**Coverage chosen on purpose**
- **Data-driven, by env.** Valid and invalid leads live in CSVs under
  `resources/test_data/<env>/`, checked against a schema when tests are collected, so a typo
  fails before a browser opens. The `prod` set is kept small so the live lead inbox isn't
  flooded, and each lead gets a unique `{run_id}` so it can be traced back to its run.
- **Negative tests are strict.** A blocked submit must flag *exactly* the expected fields, each
  with a browser message. "Didn't navigate" alone could pass for the wrong reason.
- **Known gaps fail loudly when fixed.** A name of only spaces and a phone of `call me maybe` are
  accepted by the site today. They're pinned as strict `xfail`, so the suite turns red when the
  site starts rejecting them.

**Built to be maintained**
- **Layered like a production framework:** page objects, a workflow layer, and a
  `Verifications` layer instead of bare `assert`, so every check is a named Allure step.
  Modelled on an earlier framework of mine, with one of its bugs fixed: its JSONC loader stripped
  `//` inside strings, which broke every `https://` URL.
- **Locators chosen from the real markup:** each field is found by `id`, with the exact label as
  a fallback. Placeholders were avoided because "Company name" would also match "Name".
- **Failures are easy to debug:** screenshot, URL, page HTML and browser console go into Allure,
  and Playwright traces are kept for failing tests only. CI runs lint and the full suite against
  the live site.

**Testing beyond the script**
- **Problems found while automating** are written up in
  [live site findings](docs/live-site-findings.md). The worst: the form sends name, email and
  phone in the URL, and the Website placeholder (`example.com`) is a value the field itself rejects.
- **The billing review ranks severity with stated criteria**, not by gut feel: how many customers
  are hit, whether the bug is actually visible in the mock-up, and the impact. It picks the
  US-only address over the missing CVV and explains why. One reason: PCI forbids *storing* the
  CVV but doesn't require *collecting* it. See the [billing widget review](docs/billing-widget-review.md).

## Quick start

```bash
# 1. Python environment
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Playwright browser
python3 -m playwright install --with-deps chromium

# 3. Run against the real site (default env=prod)
make test

# 4. Open the Allure report
make allure-serve
```

Optional: `cp .env.example .env` to change defaults (`ENV`, `JONES_BASE_URL`, browser channel).
