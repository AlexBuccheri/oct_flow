# Makefile for Octopus workflows Package

# Production installation
install:
	python -m pip install --upgrade pip
	python -m pip install .

# Development installation
# Install dependencies specified in .dev of pyproject.toml
install-dev: pyproject.toml
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

# Build
build:
	python -m pip install build
	python -m build

# Remove build folders
clean:
	@if [ -d ".dist" ]; then rm -r .dist; fi
	@if [ -d "src/octopus_workflows.egg-info" ]; then rm -r src/octopus_workflows.egg-info; fi

# Apply formatting
format:
	isort src/octopus_workflows
	black src/octopus_workflows
	ruff src/octopus_workflows

# Check formatting
check-format:
	ruff src/octopus_workflows
	isort --check src/octopus_workflows
	black --check src/octopus_workflows
