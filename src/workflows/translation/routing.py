"""Routing and state management nodes for the translation workflow."""

# type hints
from __future__ import annotations

# imports
from ..states import TranslationState

class FeedbackRouter:
    """Manages feedback routing and state updates"""

    def __init__(self):
        pass

    def increment_feedback(self, state: TranslationState) -> TranslationState:
        """Increment the feedback loop counter.

        Args:
            state: Current translation state

        Returns:
            Updated state with incremented feedback loop counter
        """
        if "feedback_rout_loops" not in state:
            state["feedback_rout_loops"] = 0
        state["feedback_rout_loops"] += 1
        return state
