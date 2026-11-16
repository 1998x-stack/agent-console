.PHONY: setup check docs-check test-unit test-contract test-integration test-e2e test-security compose-up compose-down

PYTHON ?= python3
NODE ?= node

setup:
	@$(PYTHON) scripts/not_implemented.py setup

check: test-unit docs-check

docs-check:
	@$(PYTHON) scripts/validate_docs.py
	@$(PYTHON) scripts/validate_phased_docs.py

test-unit:
	@$(PYTHON) -m unittest discover -s tests/unit -p 'test_*.py' -v
	@$(NODE) --test tests/node/*.test.mjs

test-contract:
	@$(PYTHON) scripts/not_implemented.py test-contract

test-integration:
	@$(PYTHON) scripts/not_implemented.py test-integration

test-e2e:
	@$(PYTHON) scripts/not_implemented.py test-e2e

test-security:
	@$(PYTHON) scripts/not_implemented.py test-security

compose-up:
	@$(PYTHON) scripts/not_implemented.py compose-up

compose-down:
	@$(PYTHON) scripts/not_implemented.py compose-down
