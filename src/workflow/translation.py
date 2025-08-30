"""Workflow definition and routing logic."""

from langgraph.graph import StateGraph, END

from ..models import TranslationState
from ..nodes import (
    style_node,
    language_detector_node,
    translator_node,
    junior_editor_node,
    fluency_editor_node,
    inc_translate_feedback_node,
)
from ..config import config

APPROVED_RESPONSE_MARKER = "approved response accepted"
STYLE_GUIDE_NEEDED = "style_guide needed"
LANGUAGE_NEEDED = "language needed"
CONTINUE = "continue"


def route_preloads(state: TranslationState) -> object:
    """Runs nodes to preload if they don't exist
    Args:
        state: Current translation state

    Returns:
        name of the next node
    """
    if "style_guide" not in state.keys():
        return STYLE_GUIDE_NEEDED
    elif "language" not in state.keys():
        return LANGUAGE_NEEDED
    else:
        return CONTINUE


def route_junior_pass(state: TranslationState) -> bool:
    """Check if junior editor approved the translation.

    Args:
        state: Current translation state

    Returns:
        True if translation is approved, False otherwise
    """
    return "approved response accepted" in state["feedback"]


def route_increment_exceed(state: TranslationState) -> bool:
    """Check if maximum feedback loops have been exceeded.

    Args:
        state: Current translation state

    Returns:
        True if max loops exceeded, False otherwise
    """
    return state["feedback_rout_loops"] >= config.max_feedback_loops


def entry_dispatcher(state: TranslationState):
    print("Dispatching...")


def create_translation_workflow():
    """Create and compile the translation workflow.

    Returns:
        Compiled workflow graph
    """
    workflow = StateGraph(TranslationState)

    # Add nodes
    workflow.add_node("entry_node", entry_dispatcher)
    workflow.add_node("style_node", style_node)
    workflow.add_node("language_detector_node", language_detector_node)
    workflow.add_node("translator_node", translator_node)
    workflow.add_node("junior_editor_node", junior_editor_node)
    workflow.add_node("inc_translate_feedback_node", inc_translate_feedback_node)
    workflow.add_node("fluency_editor_node", fluency_editor_node)

    # Set entry point
    workflow.set_entry_point("entry_node")
    workflow.add_conditional_edges(
        "entry_node",
        route_preloads,
        path_map={
            STYLE_GUIDE_NEEDED: "style_node",
            LANGUAGE_NEEDED: "language_detector_node",
            CONTINUE: "translator_node",
        },
    )

    # Add edges
    workflow.add_edge("style_node", "entry_node")
    workflow.add_edge("language_detector_node", "entry_node")
    workflow.add_edge("translator_node", "inc_translate_feedback_node")

    # Conditional routing from feedback increment
    workflow.add_conditional_edges(
        "inc_translate_feedback_node",
        route_increment_exceed,
        path_map={True: "fluency_editor_node", False: "junior_editor_node"},
    )

    # Conditional routing from junior editor
    workflow.add_conditional_edges(
        "junior_editor_node",
        route_junior_pass,
        path_map={True: "fluency_editor_node", False: "translator_node"},
    )

    # Final edge to end
    workflow.add_edge("fluency_editor_node", END)

    return workflow.compile()
