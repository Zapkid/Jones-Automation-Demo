.PHONY: install browsers test test-smoke test-regression test-call-back mock-site allure-serve allure-generate lint format clean

PY ?= python
PYTEST ?= pytest
ENV ?= prod
WORKERS ?= 1
HEADED ?=
SLOWMO ?= 0

HEADED_FLAG := $(if $(HEADED),--headed,)
# -n=1 still enables xdist and can error on Ctrl+C; only parallelize when WORKERS>1.
XDIST_FLAG := $(if $(filter 1,$(WORKERS)),,-n=$(WORKERS))

install:
	$(PY) -m pip install -e ".[dev]"

browsers:
	$(PY) -m playwright install --with-deps chromium

test:
	$(PYTEST) --env=$(ENV) --slowmo=$(SLOWMO) $(HEADED_FLAG) $(XDIST_FLAG)

test-smoke:
	$(PYTEST) -m smoke --env=$(ENV) --slowmo=$(SLOWMO) $(HEADED_FLAG) $(XDIST_FLAG)

test-regression:
	$(PYTEST) -m regression --env=$(ENV) --slowmo=$(SLOWMO) $(HEADED_FLAG) $(XDIST_FLAG)

test-call-back:
	$(PYTEST) -m call_back --env=$(ENV) --slowmo=$(SLOWMO) $(HEADED_FLAG) $(XDIST_FLAG)

mock-site:
	$(PY) -m utilities.server.mock_site

allure-generate:
	allure generate reports/allure_results -o reports/allure_report --clean

allure-serve:
	allure serve reports/allure_results

lint:
	black --check .
	isort --check-only .
	flake8 .

format:
	black .
	isort .

clean:
	rm -rf reports/allure_results reports/allure_report reports/traces reports/videos reports/screenshots
	find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +
	find . -type d -name .pytest_cache -not -path "./.venv/*" -exec rm -rf {} +
