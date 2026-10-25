# Verity — one entry point for every task. Python runs from .venv, PYTHONPATH is the repo root.
PY      ?= .venv/bin/python
NPM     ?= npm
VITE    := node frontend/node_modules/vite/bin/vite.js
export PYTHONPATH := $(CURDIR)

.PHONY: help setup data train eval fixtures models dev api web test smoke e2e ui-demo build demo-offline demo-mock lint clean

help:            ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-13s %s\n", $$1, $$2}'

setup:           ## create .venv, install Python + Node deps
	@command -v uv >/dev/null && uv venv -q --python 3.12 .venv || python3 -m venv .venv
	@command -v uv >/dev/null && uv pip install -q --python $(PY) -r requirements.txt -r requirements-dev.txt || $(PY) -m pip install -q -r requirements.txt -r requirements-dev.txt
	cd frontend && $(NPM) ci --no-audit --no-fund

data:            ## generate synthetic messages, transactions, demo feed (<1 s)
	$(PY) -m data.generators.gen_messages
	$(PY) -m data.generators.gen_transactions

train:           ## train message + transaction models
	$(PY) -m ml.message.train
	$(PY) -m ml.transaction.train

eval:            ## evaluate on held-out data -> ml/reports/
	$(PY) -m ml.eval.evaluate

fixtures:        ## record API responses for the offline mock UI
	$(PY) scripts/export_fixtures.py

models: data train eval fixtures  ## everything ML, end to end

api:             ## run the API on :8000 (auto-reload)
	$(PY) -m uvicorn backend.app.main:app --port 8000 --reload --reload-dir backend --reload-dir contracts

web:             ## run the UI dev server on :5173
	cd frontend && node node_modules/vite/bin/vite.js --port 5173

dev:             ## API + UI together (Ctrl+C stops both)
	@trap 'kill 0' INT TERM; $(MAKE) --no-print-directory api & $(MAKE) --no-print-directory web & wait

test:            ## backend tests + frontend type-check
	$(PY) -m pytest backend/tests -q
	cd frontend && npx tsc --noEmit -p tsconfig.json

smoke:           ## start API if needed, call every endpoint, validate schemas, fetch UI
	$(PY) scripts/smoke.py

e2e:             ## run docs/test_cases.csv against the API -> docs/test_results.csv + test_table.md
	$(PY) tests/e2e/run_cases.py

ui-demo:         ## walk the 3-minute demo in a real browser (needs `make dev`)
	$(PY) tests/e2e/ui_demo.py

build:           ## production build of the UI (served by the API from frontend/dist)
	cd frontend && VITE_API_URL= $(NPM) run build

demo-offline: build  ## whole product on http://localhost:8000, no internet, no API key
	ANTHROPIC_API_KEY= $(PY) -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 2

demo-mock:       ## UI only, recorded responses, no backend at all (last-resort fallback)
	cd frontend && VITE_USE_MOCKS=true node node_modules/vite/bin/vite.js --port 5173

lint:
	$(PY) -m ruff check backend ml data contracts scripts tests

clean:
	rm -rf frontend/dist .pytest_cache
