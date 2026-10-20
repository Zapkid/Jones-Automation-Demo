# Test cases

What each suite checks, and where its data comes from. Back to the [README](../README.md).

## Suites

| Suite | Data | What it checks |
| --- | --- | --- |
| `test_request_call_back.py` | `test_data/call_back_cases.jsonc` (CB1, CB2) | The exercise flow: fill, bonus 1-10 → 51-500, screenshot, submit, console.log on the thank-you page |
| `test_valid_submissions.py` | `test_data/<env>/valid_leads.csv` | Every row reaches the thank-you page (heading, subheading, *Back to Home*). The GET query echoes **every** typed value back, and console.log fires |
| `test_invalid_submissions.py` | `test_data/<env>/invalid_leads.csv` | Empty form, each required field missing, and bad email/website values. The form stays put, validation flags **exactly** the listed inputs with a message, and no console.log |
| `test_label_focus.py` | the 5 text inputs | Before the click, every label background is `none`. After clicking an input, its label is `rgba(122,184,147,1)` and the others stay `none` |

## Data by env

The CSVs are picked by `--env`, from `resources/test_data/<env>/`:

| Env | `valid_leads.csv` | `invalid_leads.csv` |
| --- | --- | --- |
| `local` | 5 rows: all four size buckets, international phone, path+query website, non-Latin name, optional fields blank | 13 rows |
| `prod` | 3 rows, kept small so the live lead inbox isn't flooded | 13 rows (validation runs in the browser, so nothing reaches the backend) |

`{run_id}` in any value expands to a unique, timestamped id per run. A row with a `known_issue`
documents something the site *should* reject but doesn't. It runs as a **strict xfail**, so the
suite turns red the day it's fixed and the row can be moved on:

- **E12**: name of only spaces passes `required`.
- **E13**: phone `call me maybe` is accepted.

Both files are schema-checked at collection: column set, unique ids, employee bucket, required
fields, and `invalid_fields` ⊆ the form's input ids.

To add a case, add a row to the CSV for that env (or an entry to `call_back_cases.jsonc` for the
exercise flow). A broken row fails collection with a message naming the file and row.
