"""Unit tests for workflow routing and state management."""

import unittest

from src.workflow.translation import (
    route_preloads,
    route_junior_pass,
    route_increment_exceed,
)
from src.nodes.translation.routing import inc_translate_feedback_node
from tests.base import BaseTranslationTest


class TestWorkflowRouting(BaseTranslationTest):
    """Test cases for workflow routing functions."""

    def test_route_preloads_needs_style_guide(self):
        """Test routing when style guide is missing."""
        state = {"text": "Sample text"}
        result = route_preloads(state)
        self.assertEqual(result, "style_guide needed")

    def test_route_preloads_needs_language(self):
        """Test routing when language is missing."""
        state = {"text": "Sample text", "style_guide": "Sample style guide"}
        result = route_preloads(state)
        self.assertEqual(result, "language needed")

    def test_route_preloads_continue(self):
        """Test routing when both style guide and language are present."""
        state = {
            "text": "Sample text",
            "style_guide": "Sample style guide",
            "language": "English",
        }
        result = route_preloads(state)
        self.assertEqual(result, "continue")

    def test_route_junior_pass_approved(self):
        """Test junior editor routing with approved feedback."""
        state = {"feedback": "approved response accepted - good translation"}
        result = route_junior_pass(state)
        self.assertTrue(result)

    def test_route_junior_pass_rejected(self):
        """Test junior editor routing with rejected feedback."""
        state = {"feedback": "This translation needs improvement"}
        result = route_junior_pass(state)
        self.assertFalse(result)

    def test_route_increment_exceed_true(self):
        """Test feedback loop limit exceeded."""
        state = {"feedback_rout_loops": 3}  # Assuming max is 3
        result = route_increment_exceed(state)
        self.assertTrue(result)

    def test_route_increment_exceed_false(self):
        """Test feedback loop limit not exceeded."""
        state = {"feedback_rout_loops": 1}
        result = route_increment_exceed(state)
        self.assertFalse(result)


class TestFeedbackIncrementNode(BaseTranslationTest):
    """Test cases for feedback increment node."""

    def test_inc_translate_feedback_node_new_counter(self):
        """Test incrementing feedback counter when not present."""
        state = {"text": "Sample text"}
        result = inc_translate_feedback_node(state)

        self.assertEqual(result["feedback_rout_loops"], 1)

    def test_inc_translate_feedback_node_existing_counter(self):
        """Test incrementing existing feedback counter."""
        state = {"feedback_rout_loops": 2}
        result = inc_translate_feedback_node(state)

        self.assertEqual(result["feedback_rout_loops"], 3)

    def test_inc_translate_feedback_node_preserves_state(self):
        """Test that increment node preserves other state values."""
        state = {"text": "Sample text", "language": "English", "feedback_rout_loops": 1}
        result = inc_translate_feedback_node(state)

        self.assertEqual(result["text"], "Sample text")
        self.assertEqual(result["language"], "English")
        self.assertEqual(result["feedback_rout_loops"], 2)


class TestWorkflowStateTransitions(BaseTranslationTest):
    """Test cases for complete workflow state transitions."""

    def test_complete_workflow_state_evolution(self):
        """Test how state evolves through workflow."""
        # Initial state
        state = {"text": "Sample text"}

        # Should need style guide first
        self.assertEqual(route_preloads(state), "style_guide needed")

        # Add style guide
        state["style_guide"] = "Sample style"
        self.assertEqual(route_preloads(state), "language needed")

        # Add language
        state["language"] = "English"
        self.assertEqual(route_preloads(state), "continue")

        # Simulate feedback loop
        state = inc_translate_feedback_node(state)
        self.assertEqual(state["feedback_rout_loops"], 1)

        # Should not exceed limit yet
        self.assertFalse(route_increment_exceed(state))

    def test_feedback_approval_workflow(self):
        """Test workflow with immediate approval."""
        state = {
            "text": "Sample text",
            "style_guide": "Sample style",
            "language": "English",
            "feedback": "approved response accepted",
        }

        # Should proceed to fluency editing
        self.assertTrue(route_junior_pass(state))


if __name__ == "__main__":
    unittest.main()
