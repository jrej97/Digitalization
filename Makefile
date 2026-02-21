PYTHON ?= python
VENV_DIR ?= .venv
VENV_PYTHON := $(VENV_DIR)/bin/python

.PHONY: venv install run test quality

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install:
	$(VENV_PYTHON) -m pip install -r requirements.txt
	$(VENV_PYTHON) -m pip install -e .

run:
	$(VENV_PYTHON) -m app.main

test:
	$(VENV_PYTHON) -m pytest -q

quality:
	$(VENV_PYTHON) scripts/quality_gate.py
