.PHONY: install-dev build-template verify-template release-dry-run publish-template-dry-run publish-template enforce-repo-policy-dry-run enforce-repo-policy test verify

PYTEST := $(PYTHON) -m pytest
DEV_REQUIREMENTS := requirements-dev.txt
TEMPLATE_REMOTE ?= reponomics-dashboard
TEMPLATE_PUBLISH_MESSAGE ?= chore: publish generated template

install-dev: install ## Install maintainer/test dependencies
	$(PIP) install -r $(DEV_REQUIREMENTS)

build-template: install ## Build the clean generated template tree in dist/template/
	$(PYTHON) scripts/build_template.py

verify-template: install ## Verify dist/template/ against the template manifest
	$(PYTHON) scripts/build_template.py --verify-only

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

verify: test release-dry-run ## Run tests and generated-output checks
