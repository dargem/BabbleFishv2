"""Factory for creating translation workflows"""

# type hints
from __future__ import annotations
from typing import TYPE_CHECKING


from typing import Dict, Any

# imports
from src.knowledge_graph import KnowledgeGraphManager
from src.providers import LLMProvider
from langgraph.graph import StateGraph, END, START
from ..states import TranslationState
from . import AbstractWorkflowFactory

from ..translation_nodes import (
    Translator,
    JuniorEditor,
    FluencyEditor,
    FeedbackRouter,
)

APPROVED_RESPONSE_MARKER = "approved response accepted"
STYLE_GUIDE_NEEDED = "style_guide needed"
LANGUAGE_NEEDED = "language needed"
CONTINUE = "continue"


class TranslationWorkflowFactory(AbstractWorkflowFactory):
    """Factory for creating translation workflows"""

    def __init__(
        self,
        llm_provider: LLMProvider,
        kg_manager: KnowledgeGraphManager,
        max_feedback_loops: int,
    ):
        self.llm_provider = llm_provider
        self.kg_manager = kg_manager
        self.max_feedback_loops = max_feedback_loops

    def create_workflow(self) -> StateGraph:
        """Create the translation workflow with all its specific logic."""
        nodes = self._create_nodes()

        workflow = StateGraph(TranslationState)
        self._add_nodes(workflow, nodes)
        self._add_routing(workflow)

        return workflow.compile()

    def _route_increment_exceed(self, state: TranslationState) -> bool:
        """Check if maximum feedback loops have been exceeded."""
        return state["feedback_rout_loops"] >= self.max_feedback_loops

    def _create_nodes(self) -> Dict[str, Any]:
        """Create all translation nodes"""  # possibly abstract this out later, have nodes get injected or use registry

        return {
            "translator": Translator(self.llm_provider).translate,
            "junior_editor": JuniorEditor(self.llm_provider).review_translation,
            "fluency_editor": FluencyEditor(self.llm_provider).improve_fluency,
            "feedback_router": FeedbackRouter().increment_feedback,
        }

    def _add_nodes(self, workflow: StateGraph, nodes):
        for key, value in nodes.items():
            # parses dict into format for entry
            workflow.add_node(key, value)

    def _add_routing(self, workflow: StateGraph):
        # Add edges
        workflow.add_edge(START, "translator")
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
            self._route_junior_pass,
            path_map={True: "fluency_editor", False: "translator"},
        )

        # Final edge to end
        workflow.add_edge("fluency_editor", END)

    def _route_junior_pass(self, state: TranslationState) -> bool:
        """Check if junior editor approved the translation.

        Args:
            state: Current translation state

        Returns:
            True if translation is approved, False otherwise
        """
        return APPROVED_RESPONSE_MARKER in state["feedback"]
