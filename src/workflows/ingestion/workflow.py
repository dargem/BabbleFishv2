"""Functional pipeline for ingestion"""

# type hints
from __future__ import annotations
from src.providers import LLMProvider
from src.knowledge_graph import KnowledgeGraphManager

# imports
from langgraph.graph import StateGraph, END
from ..states import IngestionState
from . import (
    EntityCreator,
    TripletCreator,
)


def create_ingestion_workflow(
    llm_provider: LLMProvider, kg_manager: KnowledgeGraphManager
):
    """Create and compile the ingestion workflow

    Returns:
        Compiled ingestion workflow for use
    """
    # Create nodes with injected dependencies
    entity_creator = EntityCreator(llm_provider, kg_manager)
    triplet_creator = TripletCreator(llm_provider, kg_manager)

    workflow = StateGraph(IngestionState)

    workflow.add_node("entity_addition_node", entity_creator.create_entities)
    workflow.add_node("triplet_extractor_node", triplet_creator.create_triplets)

    workflow.set_entry_point("entity_addition_node")
    workflow.add_edge("entity_addition_node", "triplet_extractor_node")
    workflow.add_edge("triplet_extractor_node", END)

    return workflow.compile()
