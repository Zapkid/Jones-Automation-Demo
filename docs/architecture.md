# Architecture

```txt
tests/call_back/test_request_call_back.py      ← intent + verifications only
        │  (parametrized from resources/test_data/call_back_cases.jsonc)
        ▼
workflows/call_back_workflow.py                ← business flow: fill → size → screenshot → submit → thank-you → console.log
        │
        ├── pages/jones/call_back/             ← CallBackPage (+ locators, types)
        └── pages/jones/thank_you/             ← ThankYouPage (+ locators)
                │
                ▼
        pages/base/base_page.py                ← goto / fill / click / select with Allure steps
```

## Layers

| Layer | Responsibility | Rule |
| --- | --- | --- |
| `tests/` | What is being verified | No selectors, no raw `assert`. Every check goes through `Verifications` so it becomes an Allure step. |
| `workflows/` | Multi-step business flows | Built only from page-object calls. Returns a typed `SubmitResult`. |
| `pages/` | One class per screen, selectors in a `*_locators.py` dataclass | Each field is resolved by its **`id`, with the exact label as fallback**, so a markup change touches one file. |
| `fixtures/` | Browser lifecycle, env, page objects, case loading | Function-scoped context/page, so each test is isolated and gets its own trace. |
| `utilities/` | Env resolution, Playwright driver, Allure helpers, JSONC loader + schema, mock server | No test logic. |
| `resources/` | Test data (`*.jsonc`) and the mock site | Cases are schema-validated at collection, so a typo fails fast with a clear message. |

## Environments

| Env | Base URL | Notes |
| --- | --- | --- |
| `prod` (default) | `https://test.netlify.app` | The site from the exercise. |
| `local` | `http://127.0.0.1:8765` | `resources/mock_site` is served automatically by the `mock_site` session fixture. Its form markup is copied verbatim from the live page (CDN assets removed), so locators and native validation match. The thank-you page is a stand-in. Runs fully offline; used by CI. |

`JONES_BASE_URL` overrides either env (for example, a Netlify deploy preview).

## Reporting

- **Allure:** feature/story labels, a step per action, the pre-submit screenshot, browser console
  log, and on failure a screenshot, URL and DOM snapshot. `environment.properties` and
  `categories.json` are written at session start. A static report is generated at session end
  when the `allure` CLI is on `PATH`.
- **Disk:** `reports/screenshots/before_submit_<run_id>.png` for every run, and
  `reports/traces/<case>_<ts>.zip` for failures (`--keep-traces` keeps all of them). Open a
  trace with `playwright show-trace`.

## "Write to console.log"

When the thank-you page is detected (URL contains `thank` **or** a heading matches
*Thank you*), `ThankYouPage.log_arrival` runs `console.log(...)` **in the browser** and writes
the same line to the Python log. The test then asserts that the line was captured from the
page's console events, so the requirement is checked, not just done.
