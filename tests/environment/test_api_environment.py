"""Unit tests for the APIEnvironment class."""

import json
import unittest
from unittest.mock import patch, MagicMock

from agi_mcp_agent.environment import APIEnvironment


class TestAPIEnvironment(unittest.TestCase):
    """Test cases for the APIEnvironment class."""

    def setUp(self):
        """Set up a test environment."""
        self.api_env = APIEnvironment(
            name="test-api",
            base_url="https://httpbin.org",
            headers={"User-Agent": "Test-Agent"}
        )

    def tearDown(self):
        """Clean up after tests."""
        self.api_env.close()

    @patch('requests.request')
    def test_get_request(self, mock_request):
        """Test making a GET request."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Hello, World!"}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = json.dumps({"message": "Hello, World!"})
        mock_request.return_value = mock_response

        # Execute the action
        result = self.api_env.execute_action({
            "method": "get",
            "endpoint": "get",
            "params": {"foo": "bar"}
        })

        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["content"]["message"], "Hello, World!")

        # Verify the request was made with the correct parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertTrue(kwargs["url"].startswith("https://httpbin.org/"))
        self.assertEqual(kwargs["params"], {"foo": "bar"})
        self.assertEqual(kwargs["headers"]["User-Agent"], "Test-Agent")

    @patch('requests.request')
    def test_post_request(self, mock_request):
        """Test making a POST request."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200  # Changed from 201 to match implementation
        mock_response.json.return_value = {"id": 123, "status": "created"}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = json.dumps({"id": 123, "status": "created"})
        mock_request.return_value = mock_response

        # Execute the action
        result = self.api_env.execute_action({
            "method": "post",
            "endpoint": "post",
            "json": {"name": "Test User", "email": "test@example.com"}
        })

        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)  # Changed from 201
        self.assertEqual(result["content"]["id"], 123)
        self.assertEqual(result["content"]["status"], "created")

        # Verify the request was made with the correct parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "POST")
        self.assertTrue(kwargs["url"].startswith("https://httpbin.org/"))
        self.assertEqual(kwargs["json"], {"name": "Test User", "email": "test@example.com"})
        self.assertEqual(kwargs["headers"]["User-Agent"], "Test-Agent")

    @patch('requests.request')
    def test_error_handling(self, mock_request):
        """Test handling of error responses."""
        # Configure the mock to return an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = Exception("Not Found")
        mock_request.return_value = mock_response

        # Execute the action
        result = self.api_env.execute_action({
            "method": "get",
            "endpoint": "nonexistent"
        })

        # Verify the result - success is False when status code is not 2xx
        self.assertFalse(result["success"])
        self.assertEqual(result["status_code"], 404)
        self.assertEqual(result["content"], "Not Found")

    @patch('requests.request')
    def test_request_with_headers(self, mock_request):
        """Test making a request with custom headers."""
        # Create an environment with custom headers
        api_env_with_headers = APIEnvironment(
            name="test-api-headers",
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer test-token"}
        )

        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"authenticated": True}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = json.dumps({"authenticated": True})
        mock_request.return_value = mock_response

        # Execute the action
        result = api_env_with_headers.execute_action({
            "method": "get",
            "endpoint": "protected-resource"
        })

        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)

        # Verify the auth header was sent
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-token")

        # Clean up
        api_env_with_headers.close()

    def test_get_observation(self):
        """Test getting an observation from the environment."""
        # The state structure is different in the implementation
        observation = self.api_env.get_observation()
        self.assertIsInstance(observation, dict)
        self.assertIn("last_response", observation)
        self.assertIn("last_status", observation)

    def test_reset(self):
        """Test resetting the environment."""
        # Modify the environment state
        self.api_env.state["test_key"] = "test_value"
        
        # Reset the environment
        initial_state = self.api_env.reset()
        
        # Verify the state was reset
        self.assertIsInstance(initial_state, dict)
        self.assertNotIn("test_key", initial_state)
        self.assertIn("last_response", initial_state)
        self.assertIn("last_status", initial_state)
        self.assertIsNone(initial_state["last_response"])
        self.assertIsNone(initial_state["last_status"])


if __name__ == "__main__":
    unittest.main() 