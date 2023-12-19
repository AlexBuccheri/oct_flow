# Makefile for Octopus workflows Package

# Specify path to virtual environment to use for this project
VENV_PATH := venv

# Ensures all commands for a given target are run in the same shell
# Necessary for running installations in the specified venv
.ONESHELL:

.PHONY: install install-dev clean

# Production installation
install:
	. $(VENV_PATH)/bin/activate
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install .

# Development installation
# Install dependencies specified in .dev of pyproject.toml
install-dev: pyproject.toml
	. $(VENV_PATH)/bin/activate
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install -e ".[dev]"

# Build
build:
	python -m pip install build
	python -m build

doc:
	cd docs && \
	sphinx-apidoc -o source ../src && \
	make html

# Remove build folders
clean:
	@if [ -d ".dist" ]; then rm -r .dist; fi
	@if [ -d "src/octopus_workflows.egg-info" ]; then rm -r src/octopus_workflows.egg-info; fi

# Clean documentation
clean-doc:
	@if [ -f "docs/source/modules.rst" ]; then rm docs/source/modules.rst; fi
	@if [ -f "docs/source/octopus_workflows.rst" ]; then rm docs/source/octopus_workflows.rst; fi
	cd docs && make clean

# Apply formatting
format:
	isort src/octopus_workflows
	black src/octopus_workflows
	ruff src/octopus_workflows

# Check formatting
check-format:
	ruff src/octopus_workflows --output-format=github
	isort --check src/octopus_workflows
	black --check src/octopus_workflows

# Run unit tests. Note, more pytest options are inherited from pyproject
# and tox options are specified in tox.ini
test:
	tox

# Run codecov
cov:
	pytest --cov=src/ --cov-report term --cov-fail-under=-1
