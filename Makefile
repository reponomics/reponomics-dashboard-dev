.DEFAULT_GOAL := help

.PHONY: help install install-dev build-template verify-template verify-workflow-classification release-dry-run publish-template-dry-run publish-template enforce-repo-policy-dry-run enforce-repo-policy test verify

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
REQUIREMENTS := requirements.txt
DEV_REQUIREMENTS := requirements-dev.txt
PYTEST := $(PYTHON) -m pytest
TEMPLATE_REMOTE ?= reponomics-dashboard
TEMPLATE_PUBLISH_MESSAGE ?= chore: publish generated template

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: $(VENV)/bin/activate ## Create the venv and install maintainer dependencies

$(VENV)/bin/activate: $(REQUIREMENTS)
	python3 -m venv $(VENV)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(VENV)/bin/activate

install-dev: install ## Install maintainer/test dependencies
	$(PIP) install -r $(DEV_REQUIREMENTS)

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

verify: test verify-workflow-classification release-dry-run ## Run tests and generated-output checks
