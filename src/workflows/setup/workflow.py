"""Factory for creating setup workflows"""
# maybe doesn't need to be factory prob one and done possibly
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config import Container

from langgraph.graph import StateGraph, END, START
from ..states import TranslationState

class SetupWorkflowFactory:
    """Factory for creating setup workflows"""
    
    def __init__(self, container: "Container"):
        self.container = container

    def create_workflow(self) -> StateGraph:
        """Creates the workflow"""

