"""Factory for creating Ingestion Workflows"""

from src.providers import LLMProvider
from src.knowledge_graph import KnowledgeGraphManager
from langgraph.graph import StateGraph, END, START
from src.workflows.states import IngestionState
from src.workflows.ingestion_nodes import (
    EntityCreator,
    TripletCreator,
)
from . import AbstractWorkflowFactory

class IngestionWorkflowFactory(AbstractWorkflowFactory):
    """Factory for creating ingestion workflows"""

    def __init__(self, llm_provider: LLMProvider, kg_manager: KnowledgeGraphManager):
        self.llm_provider = llm_provider
        self.kg_manager = kg_manager

    def create_workflow(self):
        """
        Create and compile the ingestion workflow

        Returns:
            Compiled ingestion workflow for use
        """

        # Create nodes with injected dependencies
        entity_creator = EntityCreator(self.llm_provider, self.kg_manager)
        triplet_creator = TripletCreator(self.llm_provider, self.kg_manager)

        # Add nodes
        workflow = StateGraph(IngestionState)
        workflow.add_node("entity_addition_node", entity_creator.create_entities)
        workflow.add_node("triplet_extractor_node", triplet_creator.create_triplets)

        # Route nodes
        workflow.add_edge(START, "entity_addition_node")
        workflow.add_edge("entity_addition_node", "triplet_extractor_node")
        workflow.add_edge("triplet_extractor_node", END)

        return workflow.compile()
