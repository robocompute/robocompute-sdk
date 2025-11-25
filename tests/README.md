# Tests

This directory contains test suites for the RoboCompute SDK.

## Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=robocompute --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestRoboComputeClient::test_client_initialization
```

## Test Structure

- **test_client.py** - Tests for RoboComputeClient
- **test_provider.py** - Tests for RoboComputeProvider
- **test_exceptions.py** - Tests for custom exceptions

## Test Coverage

We aim for >80% code coverage. Run `pytest --cov=robocompute --cov-report=term-missing` to see coverage details.

## Writing Tests

- Use descriptive test names
- Mock external API calls
- Test both success and error cases
- Use fixtures for common setup
- Follow AAA pattern (Arrange, Act, Assert)

## Continuous Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Multiple Python versions (3.8-3.12)
- Multiple operating systems (Linux, Windows, macOS)

