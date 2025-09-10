"""Unit tests for language detection node."""

import unittest
from unittest.mock import patch

from src.workflows.translation.language_detection import language_detector_node
from tests.base import BaseTranslationTest
from tests.fixtures import CHINESE_SAMPLE_TEXT, MINIMAL_CHINESE_TEXT


class TestLanguageDetectorNode(BaseTranslationTest):
    """Test cases for language detector node."""

    def test_language_detector_returns_language_key(self):
        """Test that language detector returns a language key in the response."""
        state = {"text": CHINESE_SAMPLE_TEXT}
        result = language_detector_node(state)

        self.assert_state_has_key(result, "language")
        self.assert_state_value_not_empty(result, "language")

    def test_language_detector_chinese_detection(self):
        """Test that Chinese text is correctly detected."""
        state = {"text": CHINESE_SAMPLE_TEXT}
        result = language_detector_node(state)

        self.assertEqual(result["language"], "Chinese")

    def test_language_detector_minimal_text(self):
        """Test language detection with minimal text."""
        state = {"text": MINIMAL_CHINESE_TEXT}
        result = language_detector_node(state)

        self.assert_state_has_key(result, "language")
        self.assertIsInstance(result["language"], str)

    def test_language_detector_empty_text_handling(self):
        """Test how language detector handles empty text."""
        state = {"text": ""}

        # This should either handle gracefully or raise a specific exception
        with self.assertRaises((ValueError, AttributeError, KeyError)):
            language_detector_node(state)

    def test_language_detector_english_text(self):
        """Test that English text is correctly detected."""
        english_text = "Hello, this is a sample English text for testing."
        state = {"text": english_text}
        result = language_detector_node(state)

        self.assertEqual(result["language"], "English")


if __name__ == "__main__":
    unittest.main()
