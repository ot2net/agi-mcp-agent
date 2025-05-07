"""Unit tests for the MemoryEnvironment class."""

import json
import os
import shutil
import tempfile
import time
import unittest
from typing import Dict, Any

from agi_mcp_agent.environment import MemoryEnvironment


class TestMemoryEnvironment(unittest.TestCase):
    """Test cases for the MemoryEnvironment class."""

    def setUp(self):
        """Set up a test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.memory_env = MemoryEnvironment(
            name="test-memory",
            storage_dir=self.test_dir
        )

    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_store_and_retrieve(self):
        """Test storing and retrieving a memory."""
        # Store a memory
        test_data = {"foo": "bar", "baz": 123}
        store_result = self.memory_env.execute_action({
            "operation": "store",
            "key": "test-key",
            "data": test_data,
            "tags": ["test", "example"]
        })
        
        # Verify store result
        self.assertTrue(store_result["success"])
        self.assertEqual(store_result["key"], "test-key")
        
        # Retrieve the memory
        retrieve_result = self.memory_env.execute_action({
            "operation": "retrieve",
            "key": "test-key"
        })
        
        # Verify retrieve result
        self.assertTrue(retrieve_result["success"])
        self.assertEqual(retrieve_result["key"], "test-key")
        self.assertEqual(retrieve_result["data"], test_data)
        self.assertEqual(retrieve_result["metadata"]["tags"], ["test", "example"])
        self.assertEqual(retrieve_result["metadata"]["access_count"], 1)

    def test_memory_expiration(self):
        """Test that memories expire correctly."""
        # Store a memory with a 1 second expiration
        self.memory_env.execute_action({
            "operation": "store",
            "key": "temp-key",
            "data": "This will expire soon",
            "expires": 1  # 1 second expiration
        })
        
        # Verify it exists initially
        retrieve_result = self.memory_env.execute_action({
            "operation": "retrieve",
            "key": "temp-key"
        })
        self.assertTrue(retrieve_result["success"])
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Verify it's gone after expiration
        retrieve_result = self.memory_env.execute_action({
            "operation": "retrieve",
            "key": "temp-key"
        })
        self.assertFalse(retrieve_result["success"])
        self.assertEqual(retrieve_result["error"], "Memory has expired")

    def test_tag_search(self):
        """Test retrieving memories by tag."""
        # Store memories with different tags
        self.memory_env.execute_action({
            "operation": "store",
            "key": "item1",
            "data": "First test item",
            "tags": ["test", "first", "example"]
        })
        
        self.memory_env.execute_action({
            "operation": "store",
            "key": "item2",
            "data": "Second test item",
            "tags": ["test", "second"]
        })
        
        self.memory_env.execute_action({
            "operation": "store",
            "key": "item3",
            "data": "Third item (not a test)",
            "tags": ["third", "example"]
        })
        
        # Search by the "test" tag
        tag_result = self.memory_env.execute_action({
            "operation": "retrieve_by_tag",
            "tag": "test"
        })
        
        # Verify tag search results
        self.assertTrue(tag_result["success"])
        self.assertEqual(tag_result["tag"], "test")
        self.assertEqual(len(tag_result["matches"]), 2)
        
        # Verify the keys are correct (order may vary)
        keys = [match["key"] for match in tag_result["matches"]]
        self.assertIn("item1", keys)
        self.assertIn("item2", keys)
        self.assertNotIn("item3", keys)

    def test_text_search(self):
        """Test searching memories by text content."""
        # Store memories with different text
        self.memory_env.execute_action({
            "operation": "store",
            "key": "note1",
            "data": "This contains apple and banana",
            "tags": ["fruit"]
        })
        
        self.memory_env.execute_action({
            "operation": "store",
            "key": "note2",
            "data": {"description": "An orange is a citrus fruit"},
            "tags": ["fruit"]
        })
        
        self.memory_env.execute_action({
            "operation": "store",
            "key": "note3",
            "data": "This is about vegetables",
            "tags": ["vegetable"]
        })
        
        # Search for fruits
        search_result = self.memory_env.execute_action({
            "operation": "search",
            "query": "fruit"
        })
        
        # Verify search results
        self.assertTrue(search_result["success"])
        self.assertEqual(len(search_result["matches"]), 2)
        
        # Search for specific fruits
        apple_search = self.memory_env.execute_action({
            "operation": "search",
            "query": "apple"
        })
        
        self.assertTrue(apple_search["success"])
        self.assertEqual(len(apple_search["matches"]), 1)
        self.assertEqual(apple_search["matches"][0]["key"], "note1")
        
    def test_persistence(self):
        """Test that memories persist to disk and can be reloaded."""
        # Store a memory
        self.memory_env.execute_action({
            "operation": "store",
            "key": "persistent-data",
            "data": {"important": True, "value": 42},
            "tags": ["persistent"]
        })
        
        # Create a new environment instance pointing to the same directory
        new_env = MemoryEnvironment(
            name="test-memory",  # Same name is important
            storage_dir=self.test_dir
        )
        
        # Retrieve the memory from the new instance
        retrieve_result = new_env.execute_action({
            "operation": "retrieve",
            "key": "persistent-data"
        })
        
        # Verify data was persisted and loaded correctly
        self.assertTrue(retrieve_result["success"])
        self.assertEqual(retrieve_result["data"]["important"], True)
        self.assertEqual(retrieve_result["data"]["value"], 42)
        self.assertEqual(retrieve_result["metadata"]["tags"], ["persistent"])
        

if __name__ == "__main__":
    unittest.main() 