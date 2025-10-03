"""Factory for annotation workflows"""
from src.providers import LLMProvider
from src.knowledge_graph import KnowledgeGraphManager
from langgraph.graph import StateGraph, START, END
from src.workflows import AnnotationState
from src.workflows.annotation_nodes import (
    EntityAnnotator, 
    HeaderCreator,
)
from . import AbstractWorkflowFactory

class AnnotationWorkflowFactory(AbstractWorkflowFactory):
    """
    Creates annotation workflows
    """
    def __init__(self, llm_provider: LLMProvider, kg: KnowledgeGraphManager):
        """
        Args:
            llm_provider: Interface for providing the llm
            kg: A facade for interfacing the graphical database
        """
        self.llm_provider = llm_provider
        self.kg = kg

        # Create objects of the used node classes
        self.entity_annotator = EntityAnnotator()
        self.header_creator = HeaderCreator()

    def create_workflow(self):
        """
        Create and compile the annotation workflow

        Returns:
            Compiled langgraph annotation workflow
        """
        workflow = StateGraph(AnnotationState)

        # Add nodes
        workflow.add_node("entity_translation_annotator", self.entity_annotator.inject_entity_translations)
        workflow.add_node("header_creator", self.header_creator.create_header)

        # Link nodes
        workflow.add_edge(START, "entity_translation_annotator")
        workflow.add_edge("entity_translation_annotator", "header_creator")
        workflow.add_edge("header_creator", END)

        return workflow.compile()