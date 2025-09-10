"""Routing and state management nodes for the translation workflow."""

from ..states import TranslationState


def inc_translate_feedback_node(state: TranslationState) -> TranslationState:
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
