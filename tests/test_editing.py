"""Unit tests for editing nodes."""

import unittest
from unittest.mock import Mock

from src.workflows.translation.editing import junior_editor_node, fluency_editor_node
from tests.base import MockLLMTestCase
from tests.fixtures import (
    CHINESE_SAMPLE_TEXT,
    ENGLISH_SAMPLE_TRANSLATION,
    MOCK_FEEDBACK_APPROVED,
    MOCK_FEEDBACK_REJECTED,
)


class TestJuniorEditorNode(MockLLMTestCase):
    """Test cases for junior editor node."""

    def test_junior_editor_returns_feedback_key(self):
        """Test that junior editor returns feedback key."""
        self.mock_llm.invoke.return_value = MOCK_FEEDBACK_APPROVED

        state = {
            "text": CHINESE_SAMPLE_TEXT,
            "translation": ENGLISH_SAMPLE_TRANSLATION,
        }
        result = junior_editor_node(state)

        self.assert_state_has_key(result, "feedback")
        self.assert_state_value_not_empty(result, "feedback")

    def test_junior_editor_approval_response(self):
        """Test junior editor with approved translation."""
        self.mock_llm.invoke.return_value = MOCK_FEEDBACK_APPROVED

        state = {
            "text": "你好，世界！",
            "translation": "Hello, world!",
        }
        result = junior_editor_node(state)

        self.assertIn("approved response accepted", result["feedback"])

    def test_junior_editor_rejection_response(self):
        """Test junior editor with rejected translation."""
        self.mock_llm.invoke.return_value = MOCK_FEEDBACK_REJECTED

        state = {
            "text": "你好，世界！",
            "translation": "Hello, world!",
        }
        result = junior_editor_node(state)

        self.assertEqual(result["feedback"], MOCK_FEEDBACK_REJECTED)
        self.assertNotIn("approved response accepted", result["feedback"])

    def test_junior_editor_prompt_includes_content(self):
        """Test that prompt includes both original text and translation."""
        self.mock_llm.invoke.return_value = "Test feedback"

        test_text = "测试文本"
        test_translation = "Test text"
        state = {"text": test_text, "translation": test_translation}

        junior_editor_node(state)

        call_args = self.mock_llm.invoke.call_args[0][0][0]
        prompt_content = call_args.content

        self.assertIn(test_text, prompt_content)
        self.assertIn(test_translation, prompt_content)

    def test_junior_editor_prompt_format(self):
        """Test that prompt contains evaluation criteria."""
        self.mock_llm.invoke.return_value = "Test feedback"

        state = {"text": "测试", "translation": "Test"}
        junior_editor_node(state)

        call_args = self.mock_llm.invoke.call_args[0][0][0]
        prompt_content = call_args.content.lower()

        # Check for evaluation criteria
        expected_criteria = ["readability", "fluency", "semantic accuracy"]
        for criterion in expected_criteria:
            self.assertIn(criterion, prompt_content)


class TestFluencyEditorNode(MockLLMTestCase):
    """Test cases for fluency editor node."""

    def test_fluency_editor_returns_fluent_translation_key(self):
        """Test that fluency editor returns fluent_translation key."""
        self.mock_llm.invoke.return_value = (
            "<index 0>\nImproved fluent text\n</index 0>"
        )

        state = {"translation": "Original translation text"}
        result = fluency_editor_node(state)

        self.assert_state_has_key(result, "fluent_translation")
        self.assert_state_value_not_empty(result, "fluent_translation")

    def test_fluency_editor_with_simple_text(self):
        """Test fluency editor with simple single paragraph text."""
        self.mock_llm.invoke.return_value = "<index 0>\nImproved version\n</index 0>"

        state = {"translation": "Simple text to improve"}
        result = fluency_editor_node(state)

        self.assertIn("Improved version", result["fluent_translation"])

    def test_fluency_editor_with_multi_paragraph_text(self):
        """Test fluency editor with multiple paragraphs."""
        self.mock_llm.invoke.return_value = (
            "<index 0>\nImproved first paragraph\n</index 0>\n"
            "<index 1>\nImproved second paragraph\n</index 1>"
        )

        state = {"translation": "First paragraph\n\nSecond paragraph"}
        result = fluency_editor_node(state)

        fluent_text = result["fluent_translation"]
        self.assertIn("Improved first paragraph", fluent_text)
        self.assertIn("Improved second paragraph", fluent_text)

    def test_fluency_editor_prompt_includes_translation(self):
        """Test that fluency editor prompt includes the translation."""
        self.mock_llm.invoke.return_value = "<index 0>\nImproved text\n</index 0>"

        test_translation = "This is a test translation to improve."
        state = {"translation": test_translation}

        fluency_editor_node(state)

        call_args = self.mock_llm.invoke.call_args[0][0][0]
        prompt_content = call_args.content

        # Should contain the tagged version of the text
        self.assertIn("<index 0>", prompt_content)
        self.assertIn(test_translation, prompt_content)

    def test_fluency_editor_prompt_format(self):
        """Test that fluency editor prompt contains proper instructions."""
        self.mock_llm.invoke.return_value = "<index 0>\nTest\n</index 0>"

        state = {"translation": "Test text"}
        fluency_editor_node(state)

        call_args = self.mock_llm.invoke.call_args[0][0][0]
        prompt_content = call_args.content.lower()

        # Check for key instructions
        expected_terms = ["proofreader", "rhythm", "flow", "index"]
        for term in expected_terms:
            self.assertIn(term, prompt_content)


class TestEditingIntegration(MockLLMTestCase):
    """Integration tests for editing nodes."""

    def test_editing_workflow_sequence(self):
        """Test that junior editor and fluency editor work in sequence."""
        # Mock junior editor response (approval)
        self.mock_llm.invoke.return_value = MOCK_FEEDBACK_APPROVED

        state = {
            "text": "你好，世界！",
            "translation": "Hello, world!",
        }

        # Run junior editor
        feedback_result = junior_editor_node(state)
        self.assertIn("approved response accepted", feedback_result["feedback"])

        # Prepare for fluency editor
        state.update(feedback_result)

        # Mock fluency editor response
        self.mock_llm.invoke.return_value = "<index 0>\nHello, world!\n</index 0>"

        # Run fluency editor
        fluency_result = fluency_editor_node(state)
        self.assertIn("fluent_translation", fluency_result)


if __name__ == "__main__":
    unittest.main()
