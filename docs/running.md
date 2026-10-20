# Running the suite

Make targets, pytest options and where artifacts land. Back to the [README](../README.md).

## Make targets

| Target | Description |
| --- | --- |
| `make install` | Editable install with dev deps |
| `make browsers` | `playwright install --with-deps chromium` |
| `make test` | Full suite |
| `make test-smoke` | `-m smoke` |
| `make test-regression` | `-m regression` |
| `make test-call-back` | `-m call_back` |
| `make allure-serve` | Open Allure report from last run |
| `make lint` / `make format` | black + isort + flake8 |

Make variables: `ENV` (default `prod`), `HEADED=1`, `SLOWMO=250`, `WORKERS=4`.

## pytest CLI

```bash
pytest \
  --env=prod \           # target env (default prod)
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

See [architecture](architecture.md#reporting) for what goes into the Allure report.
