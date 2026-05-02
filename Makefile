.DEFAULT_GOAL := help

.PHONY: help install

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
REQUIREMENTS := requirements-dev.txt

-include maintainer.mk

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: $(VENV)/bin/activate ## Create the venv and install maintainer dependencies

$(VENV)/bin/activate: $(REQUIREMENTS)
	python3 -m venv $(VENV)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(VENV)/bin/activate

