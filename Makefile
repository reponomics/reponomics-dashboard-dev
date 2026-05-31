.DEFAULT_GOAL := help

.PHONY: help clean install install-dev lock-requirements upgrade-requirements validate-requirement-locks lint typecheck test coverage build-template verify-template verify-workflow-classification sync-action-release verify-action-release template-smoke template-consumer-e2e release-dry-run publish-template-dry-run publish-template enforce-repo-policy-dry-run enforce-repo-policy verify

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTHON_MIN := 3.11
REQUIREMENTS := requirements.txt
DEV_REQUIREMENTS := requirements-dev.txt
REQUIREMENTS_LOCK := requirements.lock
DEV_REQUIREMENTS_LOCK := requirements-dev.lock
PIP_COMPILE := $(VENV)/bin/pip-compile
PIP_COMPILE_FLAGS := --generate-hashes --allow-unsafe --strip-extras --resolver=backtracking --no-header --quiet
DEV_STAMP := $(VENV)/.dev-installed
PYTEST := $(PYTHON) -m pytest
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy
COVERAGE_MIN ?= 55
COVERAGE_TARGETS := --cov=build_template --cov=publish_generated_repo --cov=verify_workflow_classification
TEMPLATE_REMOTE ?= reponomics-dashboard
TEMPLATE_PUBLISH_MESSAGE ?= chore: publish generated template
ACTION_REPO ?= ../reponomics-action
ACTION_PYTHON ?= $(ACTION_REPO)/venv/bin/python

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Remove generated build and cache artifacts (keeps venv)
	rm -rf dist output .pytest_cache .mypy_cache __pycache__ .dashboard-data-artifact
	rm -f .coverage .coverage.*
	rm -f $(DEV_STAMP)
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.log" -delete

install: $(VENV)/bin/activate ## Create the venv and install maintainer dependencies

$(VENV)/bin/activate: $(REQUIREMENTS_LOCK)
	python3 -c "import sys; min_version=(3, 11); assert sys.version_info >= min_version, f'Python {min_version[0]}.{min_version[1]}+ is required (found {sys.version.split()[0]})'"
	python3 -m venv $(VENV)
	$(PIP) install --require-hashes -r $(REQUIREMENTS_LOCK)
	touch $(VENV)/bin/activate

install-dev: $(DEV_STAMP) ## Install maintainer/test dependencies

$(DEV_STAMP): $(VENV)/bin/activate $(REQUIREMENTS) $(DEV_REQUIREMENTS) $(DEV_REQUIREMENTS_LOCK)
	$(PIP) install --require-hashes -r $(DEV_REQUIREMENTS_LOCK)
	touch $(DEV_STAMP)

lock-requirements: install-dev ## Regenerate hash-pinned dependency locks without upgrading pinned versions
	$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) --no-upgrade --output-file $(REQUIREMENTS_LOCK) $(REQUIREMENTS)
	$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) --no-upgrade --output-file $(DEV_REQUIREMENTS_LOCK) $(DEV_REQUIREMENTS)

upgrade-requirements: install-dev ## Upgrade dependency locks to latest resolvable versions
	$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) --upgrade --output-file $(REQUIREMENTS_LOCK) $(REQUIREMENTS)
	$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) --upgrade --output-file $(DEV_REQUIREMENTS_LOCK) $(DEV_REQUIREMENTS)

validate-requirement-locks: install-dev ## Verify dependency locks are current and hash-installable
	tmp_runtime_lock=$$(mktemp); \
	tmp_dev_lock=$$(mktemp); \
	cp "$(REQUIREMENTS_LOCK)" "$$tmp_runtime_lock"; \
	cp "$(DEV_REQUIREMENTS_LOCK)" "$$tmp_dev_lock"; \
	$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) --no-upgrade --output-file "$$tmp_runtime_lock" $(REQUIREMENTS); \
	$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) --no-upgrade --output-file "$$tmp_dev_lock" $(DEV_REQUIREMENTS); \
	if ! cmp -s "$(REQUIREMENTS_LOCK)" "$$tmp_runtime_lock"; then \
		echo "$(REQUIREMENTS_LOCK) is stale; run make lock-requirements"; \
		diff -u "$(REQUIREMENTS_LOCK)" "$$tmp_runtime_lock" || true; \
		rm -f "$$tmp_runtime_lock" "$$tmp_dev_lock"; \
		exit 1; \
	fi; \
	if ! cmp -s "$(DEV_REQUIREMENTS_LOCK)" "$$tmp_dev_lock"; then \
		echo "$(DEV_REQUIREMENTS_LOCK) is stale; run make lock-requirements"; \
		diff -u "$(DEV_REQUIREMENTS_LOCK)" "$$tmp_dev_lock" || true; \
		rm -f "$$tmp_runtime_lock" "$$tmp_dev_lock"; \
		exit 1; \
	fi; \
	rm -f "$$tmp_runtime_lock" "$$tmp_dev_lock"
	tmp_runtime_site=$$(mktemp -d); \
	tmp_dev_site=$$(mktemp -d); \
	$(PYTHON) -m pip install --require-hashes --target "$$tmp_runtime_site" -r $(REQUIREMENTS_LOCK); \
	$(PYTHON) -m pip install --require-hashes --target "$$tmp_dev_site" -r $(DEV_REQUIREMENTS_LOCK); \
	rm -rf "$$tmp_runtime_site" "$$tmp_dev_site"

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

sync-action-release: install ## Sync template refs to ACTION_TAG from reponomics-dashboard-action
	@test -n "$(ACTION_TAG)" || { echo "ACTION_TAG is required, for example ACTION_TAG=v0.16.0"; exit 1; }
	$(PYTHON) scripts/sync_action_release.py sync --tag "$(ACTION_TAG)"

verify-action-release: install ## Verify template action release refs and metadata
	$(PYTHON) scripts/sync_action_release.py verify

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

coverage: install-dev ## Run tests with coverage gate for maintainer scripts
	$(PYTEST) tests/ -v $(COVERAGE_TARGETS) --cov-report=term-missing --cov-fail-under=$(COVERAGE_MIN)

template-smoke: build-template ## Smoke-test ephemeral template publish and generated workflows
	$(PYTHON) scripts/smoke_template_release.py --output dist/template

template-consumer-e2e: build-template ## Run generated template consumers against a local action runtime
	$(PYTHON) scripts/template_consumer_e2e.py --template-dir dist/template --action-repo $(ACTION_REPO) --action-python $(ACTION_PYTHON)

verify: validate-requirement-locks lint typecheck coverage verify-workflow-classification verify-action-release release-dry-run template-smoke ## Run lint, type checks, coverage, dependency-lock, and generated-output checks
