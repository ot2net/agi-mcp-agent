# Testing Environment Implementations

This document outlines the testing approach for the AGI-MCP-Agent environment implementations, providing guidance on unit testing, integration testing, and manual verification.

## Overview

Testing environments requires a balance between unit tests for specific functionality and integration tests for real-world behavior. Since many environments connect to external systems, we employ a combination of testing approaches:

1. Unit tests with mocking
2. Integration tests with real but controlled external systems
3. Example scripts for manual verification
4. Automated test coverage analysis

## Unit Testing

Each environment class has corresponding unit tests in the `tests/environment/` directory. The basic pattern for unit testing environments is:

```python
import unittest
from agi_mcp_agent.environment import SomeEnvironment

class TestSomeEnvironment(unittest.TestCase):
    def setUp(self):
        # Initialize the environment with test parameters
        self.env = SomeEnvironment(name="test-env", ...)
        
    def tearDown(self):
        # Clean up resources
        self.env.close()
        
    def test_some_operation(self):
        # Test a specific operation
        result = self.env.execute_action({
            "operation": "some_operation",
            "param1": "value1"
        })
        
        # Assert expected outcomes
        self.assertTrue(result["success"])
        self.assertEqual(result["some_key"], "expected_value")
```

### Mocking External Dependencies

For environments that depend on external systems (APIs, databases, etc.), use mocking to isolate tests:

```python
from unittest import mock
import requests

class TestAPIEnvironment(unittest.TestCase):
    @mock.patch('requests.get')
    def test_get_request(self, mock_get):
        # Configure the mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response
        
        # Execute test
        result = self.api_env.execute_action({
            "operation": "get",
            "url": "https://example.com/api"
        })
        
        # Verify the mock was called correctly
        mock_get.assert_called_once_with(
            "https://example.com/api", 
            headers=mock.ANY, 
            params=None
        )
        
        # Assert the result was processed correctly
        self.assertTrue(result["success"])
        self.assertEqual(result["content"]["key"], "value")
```

## Integration Testing

While unit tests provide good coverage of logic, integration tests ensure environments work properly with real external systems.

### Controlled External Systems

For integration tests, use:

- Local in-memory SQLite for database tests
- Local file system in a temporary directory
- Public APIs with stable endpoints (e.g., httpbin.org)
- Docker containers for more complex services

### Example Integration Test

```python
import tempfile
import shutil
import unittest
from agi_mcp_agent.environment import FileSystemEnvironment

class TestFileSystemIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.fs_env = FileSystemEnvironment(
            name="test-fs",
            root_dir=self.test_dir
        )
        
    def tearDown(self):
        # Clean up
        self.fs_env.close()
        shutil.rmtree(self.test_dir)
        
    def test_file_operations_integration(self):
        # Test writing a file
        write_result = self.fs_env.execute_action({
            "operation": "write_file",
            "path": "test.txt",
            "content": "Hello, World!"
        })
        self.assertTrue(write_result["success"])
        
        # Test reading the file
        read_result = self.fs_env.execute_action({
            "operation": "read_file",
            "path": "test.txt"
        })
        self.assertTrue(read_result["success"])
        self.assertEqual(read_result["content"], "Hello, World!")
```

## Example Scripts

Example scripts in the `examples/` directory provide both documentation and a way to manually verify environment functionality:

- `environment_usage.py`: Demonstrates all environment types
- `memory_environment_usage.py`: Focuses on the memory environment
- Other specific environment examples

To run an example:

```bash
# Using Python directly
python examples/environment_usage.py

# Using Poetry
poetry run python examples/environment_usage.py
```

## Test Coverage

We use `pytest-cov` to track test coverage for environment implementations:

```bash
# Run tests with coverage analysis
poetry run pytest --cov=agi_mcp_agent.environment tests/environment/

# Generate an HTML coverage report
poetry run pytest --cov=agi_mcp_agent.environment --cov-report=html tests/environment/
```

### Coverage Targets

Target coverage levels for environment implementations:

- Core functionality: 90%+ coverage
- Error handling paths: 80%+ coverage
- Edge cases: 70%+ coverage

## Environment-Specific Testing Considerations

### API Environment

- Test with different HTTP methods (GET, POST, PUT, DELETE)
- Test authentication mechanisms
- Test error handling (4xx, 5xx responses)
- Test with binary and text responses

### Filesystem Environment

- Test with various file types (text, binary)
- Test path sanitization and security
- Test error conditions (permissions, disk full)
- Test with large files

### Web Environment

- Test with different web page structures
- Test content extraction with various selectors
- Test navigation and state management
- Test error handling for unavailable pages

### Database Environment

- Test with different query types (SELECT, INSERT, UPDATE)
- Test transaction handling
- Test connection pooling
- Test with various data types

### Memory Environment

- Test persistence across environment instances
- Test expiration mechanisms
- Test search and retrieval operations
- Test concurrent access patterns

### MCP Environment

- Test server lifecycle management
- Test tool discovery and invocation
- Test error handling for unavailable tools
- Test with various server configurations

## Running Tests with Poetry

The recommended way to run tests is using Poetry:

```bash
# Run all environment tests
poetry run pytest tests/environment/

# Run tests for a specific environment
poetry run pytest tests/environment/test_memory_environment.py

# Run a specific test
poetry run pytest tests/environment/test_api_environment.py::TestAPIEnvironment::test_get_request
``` 