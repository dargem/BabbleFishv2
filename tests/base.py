"""Base test class and utilities for translation tests."""

import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.models import TranslationState


class BaseTranslationTest(unittest.TestCase):
    """Base test class for translation node tests."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_llm = Mock()
        self.mock_llm.invoke.return_value = "Mock LLM response"

    def create_test_state(self, **kwargs) -> TranslationState:
        """Create a test state with default values."""
        default_state = {
            "text": "Test text",
            "language": "English",
            "translation": "Test translation",
            "style_guide": "Test style guide",
            "fluent_translation": "Test fluent translation",
            "feedback": "Test feedback",
            "feedback_rout_loops": 0,
        }
        default_state.update(kwargs)
        return default_state

    def assert_state_has_key(self, state: Dict[str, Any], key: str):
        """Assert that state contains the expected key."""
        self.assertIn(key, state, f"State should contain key: {key}")

    def assert_state_value_not_empty(self, state: Dict[str, Any], key: str):
        """Assert that state value is not empty."""
        self.assertIn(key, state)
        self.assertTrue(state[key], f"State value for {key} should not be empty")


class MockLLMTestCase(BaseTranslationTest):
    """Test case with mocked LLM for faster testing."""

    def setUp(self):
        """Set up mocked LLM."""
        super().setUp()
        self.llm_patcher = patch("src.config.config.get_llm")
        self.mock_get_llm = self.llm_patcher.start()
        self.mock_get_llm.return_value = self.mock_llm

    def tearDown(self):
        """Clean up patches."""
        self.llm_patcher.stop()
        super().tearDown()
