"""Integration tests for complete translation workflow."""

import unittest
from unittest.mock import patch, Mock
import os

from src.workflow.translation import create_translation_workflow
from tests.base import BaseTranslationTest
from tests.fixtures import CHINESE_SAMPLE_TEXT


class TestTranslationWorkflow(BaseTranslationTest):
    """Integration tests for the complete translation workflow."""

    @patch("src.config.config.get_llm")
    def test_workflow_creation(self, mock_get_llm):
        """Test that workflow can be created successfully."""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm

        workflow = create_translation_workflow()
        self.assertIsNotNone(workflow)

    @patch("src.config.config.get_llm")
    def test_workflow_execution_with_mocks(self, mock_get_llm):
        """Test workflow execution with mocked LLM responses."""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm

        # Mock LLM responses for different nodes
        mock_responses = [
            "Test style guide",
            "English",  # Language detection
            "Test translation",
            "approved response accepted",
            "Improved fluent translation",
        ]
        # Use itertools.cycle to handle multiple calls
        import itertools

        mock_llm.invoke.side_effect = itertools.cycle(mock_responses)

        workflow = create_translation_workflow()

        initial_state = {"text": CHINESE_SAMPLE_TEXT}
        result = workflow.invoke(initial_state)

        # Check that all expected keys are present
        expected_keys = [
            "text",
            "style_guide",
            "language",
            "translation",
            "feedback",
            "fluent_translation",
        ]
        for key in expected_keys:
            self.assertIn(key, result, f"Result should contain {key}")

    @patch("src.config.config.get_llm")
    def test_workflow_feedback_loop(self, mock_get_llm):
        """Test workflow with feedback rejection and retry."""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm

        # Mock responses: style, language, translation, rejection, improved translation, approval, fluency
        mock_responses = [
            "Test style guide",
            "English",
            "Initial translation",
            "Needs improvement - rejected",  # First rejection
            "Improved translation",
            "approved response accepted",  # Approval
            "Final fluent translation",
        ]
        # Use itertools.cycle to handle multiple calls
        import itertools

        mock_llm.invoke.side_effect = itertools.cycle(mock_responses)

        workflow = create_translation_workflow()

        initial_state = {"text": "Test text"}
        result = workflow.invoke(initial_state)

        # Should have gone through feedback loop
        self.assertGreater(result.get("feedback_rout_loops", 0), 1)
        self.assertIn("fluent_translation", result)

    @patch("src.config.config.get_llm")
    def test_workflow_max_feedback_loops(self, mock_get_llm):
        """Test workflow hitting maximum feedback loops."""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm

        # Mock continuous rejection until max loops
        mock_responses = [
            "Test style guide",
            "English",
            "Translation attempt 1",
            "Rejected - needs improvement",
            "Translation attempt 2",
            "Rejected - still needs work",
            "Translation attempt 3",
            "Rejected - final attempt",
            "Final fluent translation",  # Should go to fluency editor after max loops
        ]
        # Use itertools.cycle to handle multiple calls
        import itertools

        mock_llm.invoke.side_effect = itertools.cycle(mock_responses)

        workflow = create_translation_workflow()

        initial_state = {"text": "Test text"}
        result = workflow.invoke(initial_state)

        # Should have hit max feedback loops
        self.assertEqual(result.get("feedback_rout_loops"), 3)
        self.assertIn("fluent_translation", result)


class TestWorkflowNodes(BaseTranslationTest):
    """Test individual workflow node behavior."""

    def test_workflow_has_all_required_nodes(self):
        """Test that workflow contains all required nodes."""
        with patch("src.config.config.get_llm") as mock_get_llm:
            mock_get_llm.return_value = Mock()
            workflow = create_translation_workflow()

            # Get the graph representation
            graph = workflow.get_graph()
            nodes = list(graph.nodes.keys())  # Get node names directly

            expected_nodes = [
                "entry_node",
                "style_node",
                "language_detector_node",
                "translator_node",
                "junior_editor_node",
                "inc_translate_feedback_node",
                "fluency_editor_node",
            ]

            for node in expected_nodes:
                self.assertIn(node, nodes, f"Workflow should contain {node}")

    @unittest.skipUnless(os.getenv("RUN_INTEGRATION_TESTS"), "Integration tests skipped by default")
    def test_full_workflow_integration(self):
        """Full integration test with real LLM (expensive - skipped by default)."""
        workflow = create_translation_workflow()

        initial_state = {"text": "你好，世界！这是一个测试。"}  # Simple Chinese text
        result = workflow.invoke(initial_state)

        # Verify complete workflow execution
        self.assertIn("style_guide", result)
        self.assertIn("language", result)
        self.assertIn("translation", result)
        self.assertIn("fluent_translation", result)

        # Verify content quality
        self.assertEqual(result["language"], "Chinese")
        self.assertIsInstance(result["translation"], str)
        self.assertGreater(len(result["translation"]), 0)
        
        # Print results for verification
        print(f"\n{'='*50}")
        print("INTEGRATION TEST RESULTS")
        print(f"{'='*50}")
        print(f"Original text: {initial_state['text']}")
        print(f"Detected language: {result['language']}")
        print(f"Translation: {result['translation']}")
        print(f"Fluent translation: {result['fluent_translation']}")
        print(f"Style guide length: {len(result['style_guide'])} characters")
        print(f"{'='*50}")


if __name__ == "__main__":
    unittest.main()
