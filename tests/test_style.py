"""Unit tests for style guide generation."""

import os
import unittest

from workflows.setup.style import style_node
from tests.base import MockLLMTestCase
from tests.fixtures import CHINESE_SAMPLE_TEXT, MOCK_STYLE_GUIDE


class TestStyleNode(MockLLMTestCase):
    """Test cases for style guide generation node."""

    def test_style_node_returns_style_guide_key(self):
        """Test that style node returns style_guide key."""
        self.mock_llm.invoke.return_value = MOCK_STYLE_GUIDE

        state = {"text": CHINESE_SAMPLE_TEXT}
        result = style_node(state)

        self.assert_state_has_key(result, "style_guide")
        self.assert_state_value_not_empty(result, "style_guide")

    def test_style_node_content_structure(self):
        """Test that style guide contains expected sections."""
        self.mock_llm.invoke.return_value = MOCK_STYLE_GUIDE

        state = {"text": CHINESE_SAMPLE_TEXT}
        result = style_node(state)

        style_guide = result["style_guide"]
        # Check for expected sections
        self.assertIn("Genre", style_guide)
        self.assertIn("Literary Style", style_guide)

    def test_style_node_prompt_includes_text(self):
        """Test that the prompt includes the input text."""
        self.mock_llm.invoke.return_value = MOCK_STYLE_GUIDE

        test_text = "This is a test text for style analysis."
        state = {"text": test_text}
        style_node(state)

        call_args = self.mock_llm.invoke.call_args[0][0][0]
        prompt_content = call_args.content
        self.assertIn(test_text, prompt_content)

    def test_style_node_prompt_format(self):
        """Test that the prompt is properly formatted."""
        self.mock_llm.invoke.return_value = MOCK_STYLE_GUIDE

        state = {"text": "Sample text"}
        style_node(state)

        call_args = self.mock_llm.invoke.call_args[0][0][0]
        prompt_content = call_args.content

        # Check for key prompt elements
        self.assertIn("literary analyst", prompt_content.lower())
        self.assertIn("style guide", prompt_content.lower())
        self.assertIn("translation", prompt_content.lower())

    def test_style_node_with_different_text_types(self):
        """Test style node with different types of text."""
        test_cases = [
            "Simple dialogue text",
            "Descriptive narrative with complex sentences and detailed imagery.",
            "Action-packed scene with short, punchy sentences. Bang! Crash!",
        ]

        for test_text in test_cases:
            with self.subTest(text_type=test_text[:20]):
                self.mock_llm.invoke.return_value = f"Style guide for: {test_text[:20]}"

                state = {"text": test_text}
                result = style_node(state)

                self.assert_state_has_key(result, "style_guide")
                self.assertIn(test_text[:15], result["style_guide"])


class TestStyleIntegration(unittest.TestCase):
    """Integration tests for style node."""

    @unittest.skipUnless(
        os.getenv("RUN_INTEGRATION_TESTS"), "Integration tests skipped by default"
    )
    def test_style_node_real_analysis(self):
        """Integration test with real LLM analysis."""
        state = {"text": CHINESE_SAMPLE_TEXT}
        result = style_node(state)

        self.assertIn("style_guide", result)
        style_guide = result["style_guide"]

        # Should be substantial content
        self.assertGreater(len(style_guide), 100)

        # Should contain analysis keywords
        analysis_keywords = ["genre", "style", "tone", "mood"]
        style_guide_lower = style_guide.lower()
        found_keywords = [kw for kw in analysis_keywords if kw in style_guide_lower]
        self.assertGreater(
            len(found_keywords),
            1,
            f"Style guide should contain analysis keywords, found: {found_keywords}",
        )


if __name__ == "__main__":
    unittest.main()
