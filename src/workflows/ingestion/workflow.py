"""Functional pipeline for ingestion"""

# type hints
from __future__ import annotations
from src.providers import LLMProvider
from src.knowledge_graph import KnowledgeGraphManager

# imports
from langgraph.graph import StateGraph, END
from ..states import IngestionState
from . import (
    entity_addition_node,
    triplet_extractor_node,
)


def create_ingestion_workflow(
    llm_provider: LLMProvider, kg_manager: KnowledgeGraphManager
):
    """Create and compile the ingestion workflow

    Returns:
        Compiled ingestion workflow for use
    """
    workflow = StateGraph(IngestionState)

    workflow.add_node("entity_addition_node", entity_addition_node)
    workflow.add_node("triplet_extractor_node", triplet_extractor_node)

    workflow.set_entry_point("entity_addition_node")
    workflow.add_edge("entity_addition_node", "triplet_extractor_node")
    workflow.add_edge("triplet_extractor_node", END)

    return workflow.compile()
