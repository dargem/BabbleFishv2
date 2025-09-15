"""Factory for creating translation workflows"""

# type hints
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config import Container
from typing import Dict, Any

# imports
from langgraph.graph import StateGraph, END, START
from ..states import TranslationState

from . import (
    StyleAnalyzer,
    LanguageDetector,
    Translator,
    JuniorEditor,
    FluencyEditor,
    FeedbackRouter,
)

APPROVED_RESPONSE_MARKER = "approved response accepted"
STYLE_GUIDE_NEEDED = "style_guide needed"
LANGUAGE_NEEDED = "language needed"
CONTINUE = "continue"


def route_junior_pass(state: TranslationState) -> bool:
    """Check if junior editor approved the translation.

    Args:
        state: Current translation state

    Returns:
        True if translation is approved, False otherwise
    """
    return APPROVED_RESPONSE_MARKER in state["feedback"]


def route_increment_exceed(state: TranslationState, container: "Container") -> bool:
    """Check if maximum feedback loops have been exceeded.

    Args:
        state: Current translation state
        container: Container instance

    Returns:
        True if max loops exceeded, False otherwise
    """
    return (
        state["feedback_rout_loops"]
        >= container.get_stats()["config"]["max_feedback_loops"]
    )


class TranslationWorkflowFactory:
    """Factory for creating translation workflows"""

    def __init__(self, container: "Container"):
        self.container = container

    def create_workflow(self) -> StateGraph:
        """Create the translation workflow with all its specific logic."""
        # Create nodes with dependencies from container
        nodes = self._create_nodes()

        workflow = StateGraph(TranslationState)
        self._add_nodes(workflow, nodes)
        self._add_routing(workflow)

        return workflow.compile()

    def _route_increment_exceed(self, state: TranslationState) -> bool:
        """Check if maximum feedback loops have been exceeded."""
        return (
            state["feedback_rout_loops"]
            >= self.container._config.workflow.max_feedback_loops
        )

    def _create_nodes(self) -> Dict[str, Any]:
        """Create all translation nodes"""  # possibly abstract this out later, have nodes get injected or use registry
        llm_provider = self.container.get_llm_provider()

        return {
            "style_analyzer": StyleAnalyzer(llm_provider).analyze_style,
            "language_detector": LanguageDetector().detect_language,
            "translator": Translator(llm_provider).translate,
            "junior_editor": JuniorEditor(llm_provider).review_translation,
            "fluency_editor": FluencyEditor(llm_provider).improve_fluency,
            "feedback_router": FeedbackRouter().increment_feedback,
        }

    def _add_nodes(self, workflow: StateGraph, nodes):
        for key, value in nodes.items():
            # parses dict into format for entry
            workflow.add_node(key, value)

    def _add_routing(self, workflow: StateGraph):
        # Add edges
        workflow.add_edge(START, "style_analyzer")
        workflow.add_edge("style_analyzer", "language_detector")
        workflow.add_edge("language_detector", "translator")
        workflow.add_edge("translator", "feedback_router")

        # Conditional routing from feedback increment
        workflow.add_conditional_edges(
            "feedback_router",
            self._route_increment_exceed,
            path_map={True: "fluency_editor", False: "junior_editor"},
        )

        # Conditional routing from junior editor
        workflow.add_conditional_edges(
            "junior_editor",
            route_junior_pass,
            path_map={True: "fluency_editor", False: "translator"},
        )

        # Final edge to end
        workflow.add_edge("fluency_editor", END)
