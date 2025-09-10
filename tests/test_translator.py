"""Unit tests for translation node."""

import unittest
import os
from unittest.mock import Mock

from src.workflows.translation.translator import translator_node
from tests.base import MockLLMTestCase
from tests.fixtures import (
    CHINESE_SAMPLE_TEXT,
    ENGLISH_SAMPLE_TRANSLATION,
    MINIMAL_CHINESE_TEXT,
)


class TestTranslatorNode(MockLLMTestCase):
    """Test cases for translator node."""

    def test_translator_returns_translation_key(self):
        """Test that translator returns a translation key."""
        self.mock_llm.invoke.return_value = "Mock translation"

        state = self.create_test_state(text=CHINESE_SAMPLE_TEXT, language="Chinese")
        result = translator_node(state)

        self.assert_state_has_key(result, "translation")
        self.assert_state_value_not_empty(result, "translation")

    def test_translator_initial_translation(self):
        """Test initial translation without feedback."""
        expected_translation = "This is a mock translation"
        self.mock_llm.invoke.return_value = expected_translation

        state = {"text": MINIMAL_CHINESE_TEXT, "language": "Chinese"}
        result = translator_node(state)

        self.assertEqual(result["translation"], expected_translation)
        self.mock_llm.invoke.assert_called_once()

    def test_translator_with_feedback(self):
        """Test translation with feedback iteration."""
        improved_translation = "This is an improved translation"
        self.mock_llm.invoke.return_value = improved_translation

        state = {
            "text": MINIMAL_CHINESE_TEXT,
            "language": "Chinese",
            "translation": "Previous translation",
            "feedback": "Please improve the flow",
        }
        result = translator_node(state)

        self.assertEqual(result["translation"], improved_translation)
        # Verify the prompt includes feedback
        call_args = self.mock_llm.invoke.call_args[0][0][0]
        self.assertIn("feedback", call_args.content.lower())

    def test_translator_prompt_format(self):
        """Test that translator creates proper prompt format."""
        self.mock_llm.invoke.return_value = "Mock translation"

        state = {"text": "测试文本", "language": "Chinese"}
        translator_node(state)

        # Verify LLM was called with a message
        self.mock_llm.invoke.assert_called_once()
        call_args = self.mock_llm.invoke.call_args[0][0]
        self.assertEqual(len(call_args), 1)  # Should be a list with one message

    def test_translator_language_in_prompt(self):
        """Test that the detected language is included in the prompt."""
        self.mock_llm.invoke.return_value = "Mock translation"

        state = {"text": "测试文本", "language": "Chinese"}
        translator_node(state)

        call_args = self.mock_llm.invoke.call_args[0][0][0]
        prompt_content = call_args.content
        self.assertIn("Chinese", prompt_content)


class TestTranslatorIntegration(unittest.TestCase):
    """Integration tests for translator node (requires actual LLM)."""

    @unittest.skipUnless(
        os.getenv("RUN_INTEGRATION_TESTS"), "Integration tests skipped by default"
    )
    def test_translator_real_translation(self):
        """Integration test with real LLM."""
        state = {"text": MINIMAL_CHINESE_TEXT, "language": "Chinese"}
        result = translator_node(state)

        self.assertIn("translation", result)
        self.assertIsInstance(result["translation"], str)
        self.assertTrue(len(result["translation"]) > 0)

        # Print for verification
        print(f"\nOriginal: {state['text']}")
        print(f"Translation: {result['translation']}")


if __name__ == "__main__":
    unittest.main()
