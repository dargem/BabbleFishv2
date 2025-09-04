"""Functional pipeline for ingestion"""

from langgraph.graph import StateGraph, END

from ..models import IngestionState


from ..nodes.ingestion import (
    entity_addition_node,
    triplet_extractor_node,
)


def create_ingestion_workflow():
    """Create and compile the ingestion workflow

    Returns:
        Compiled ingestion workflow for use
    """
    workflow = StateGraph(IngestionState)

    workflow.add_node("entity_addition_node", entity_addition_node)
    workflow.add_node("triplet_extractor_node", triplet_extractor_node)
