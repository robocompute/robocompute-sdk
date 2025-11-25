.PHONY: help install install-dev test lint format clean build publish

help:
	@echo "Available commands:"
	@echo "  make install      - Install package"
	@echo "  make install-dev  - Install package with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build package"
	@echo "  make publish      - Publish to PyPI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install pytest pytest-cov pytest-mock black flake8 mypy

test:
	pytest tests/ -v

lint:
	flake8 robocompute tests
	mypy robocompute

format:
	black robocompute tests examples

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/

build:
	python -m build

publish: build
	twine upload dist/*

