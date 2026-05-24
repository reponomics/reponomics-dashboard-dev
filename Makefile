.DEFAULT_GOAL := help

.PHONY: help clean install install-dev lint typecheck build-template verify-template verify-workflow-classification release-dry-run publish-template-dry-run publish-template enforce-repo-policy-dry-run enforce-repo-policy test verify

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTHON_MIN := 3.11
REQUIREMENTS := requirements.txt
DEV_REQUIREMENTS := requirements-dev.txt
DEV_STAMP := $(VENV)/.dev-installed
PYTEST := $(PYTHON) -m pytest
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy
TEMPLATE_REMOTE ?= reponomics-dashboard
TEMPLATE_PUBLISH_MESSAGE ?= chore: publish generated template

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Remove generated build and cache artifacts (keeps venv)
	rm -rf dist output .pytest_cache .mypy_cache __pycache__ .traffic-artifact
	rm -f $(DEV_STAMP)
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.log" -delete

install: $(VENV)/bin/activate ## Create the venv and install maintainer dependencies

$(VENV)/bin/activate: $(REQUIREMENTS)
	python3 -c "import sys; min_version=(3, 11); assert sys.version_info >= min_version, f'Python {min_version[0]}.{min_version[1]}+ is required (found {sys.version.split()[0]})'"
	python3 -m venv $(VENV)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(VENV)/bin/activate

install-dev: $(DEV_STAMP) ## Install maintainer/test dependencies

$(DEV_STAMP): $(VENV)/bin/activate $(REQUIREMENTS) $(DEV_REQUIREMENTS)
	$(PIP) install -r $(DEV_REQUIREMENTS)
	touch $(DEV_STAMP)

lint: install-dev ## Run static lint checks
	$(RUFF) check scripts tests

typecheck: install-dev ## Run static type checks
	$(MYPY) --python-version $(PYTHON_MIN) scripts tests

build-template: install ## Build the clean generated template tree in dist/template/
	$(PYTHON) scripts/build_template.py

verify-template: install ## Verify dist/template/ against the template manifest
	$(PYTHON) scripts/build_template.py --verify-only

verify-workflow-classification: install ## Verify maintainer vs template workflow boundaries
	$(PYTHON) scripts/verify_workflow_classification.py

release-dry-run: build-template ## Build generated template artifact locally

publish-template-dry-run: build-template ## Show the generated template publish target without pushing
	$(PYTHON) scripts/publish_generated_repo.py --output dist/template --remote $(TEMPLATE_REMOTE) --branch main --expected-repo reponomics/reponomics-dashboard --message "$(TEMPLATE_PUBLISH_MESSAGE)"

publish-template: build-template ## Publish dist/template/ to the template repository main branch
	$(PYTHON) scripts/publish_generated_repo.py --output dist/template --remote $(TEMPLATE_REMOTE) --branch main --expected-repo reponomics/reponomics-dashboard --message "$(TEMPLATE_PUBLISH_MESSAGE)" --push

enforce-repo-policy-dry-run: install ## Show GitHub repository settings changes without applying them
	$(PYTHON) scripts/enforce_repository_policy.py --dry-run

enforce-repo-policy: install ## Enforce GitHub repository feature, workflow, and security settings
	$(PYTHON) scripts/enforce_repository_policy.py

test: install-dev ## Run the Python test suite (maintainer path)
	$(PYTEST) tests/ -v

verify: lint typecheck test verify-workflow-classification release-dry-run ## Run lint, type checks, tests, and generated-output checks
