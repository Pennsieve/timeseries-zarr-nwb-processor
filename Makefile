.PHONY: help run clean venv install test test-cov lint typecheck check pre-commit

VENV_DIR      ?= venv
PYTHON        ?= python3
LIBRARY       ?= ../timeseries-zarr-py
CONVERTER     ?= ../timeseries-zarr-nwb

.DEFAULT: help

help:
	@echo "Make Help for timeseries-zarr-nwb-processor"
	@echo ""
	@echo "make venv       - create virtual environment and install all dependencies"
	@echo "make install    - install dependencies into existing venv"
	@echo "make pre-commit - install pre-commit hooks"
	@echo "make test       - run tests"
	@echo "make test-cov   - run tests with coverage report"
	@echo "make lint       - run linter + formatter with auto-fix"
	@echo "make typecheck  - run mypy --strict"
	@echo "make check      - run lint check, typecheck, and tests"
	@echo "make run        - run the processor locally with docker-compose"
	@echo "make clean      - remove all files from locally mounted input / output directories"

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install --config-settings editable_mode=strict -e $(LIBRARY) -e $(CONVERTER) -e ".[test,dev]"
	@echo ""
	@echo "Virtual environment created. Activate with:"
	@echo "  source $(VENV_DIR)/bin/activate"

install:
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install --config-settings editable_mode=strict -e $(LIBRARY) -e $(CONVERTER) -e ".[test,dev]"

test:
	$(VENV_DIR)/bin/python -m pytest tests/ -v

test-cov:
	$(VENV_DIR)/bin/python -m pytest tests/ -v --cov=timeseries_zarr_nwb_processor --cov-report=term-missing

lint:
	$(VENV_DIR)/bin/ruff check --fix timeseries_zarr_nwb_processor/ tests/
	$(VENV_DIR)/bin/ruff format timeseries_zarr_nwb_processor/ tests/

typecheck:
	$(VENV_DIR)/bin/mypy timeseries_zarr_nwb_processor/

check:
	$(VENV_DIR)/bin/ruff check timeseries_zarr_nwb_processor/ tests/
	$(VENV_DIR)/bin/ruff format --check timeseries_zarr_nwb_processor/ tests/
	$(VENV_DIR)/bin/mypy timeseries_zarr_nwb_processor/
	$(VENV_DIR)/bin/python -m pytest tests/

pre-commit:
	$(VENV_DIR)/bin/pre-commit install

run:
	docker-compose -f docker-compose.yml down --remove-orphans
	docker-compose -f docker-compose.yml build
	docker-compose -f docker-compose.yml up --exit-code-from writer

clean:
	rm -f data/input/*
	rm -rf data/output/*
