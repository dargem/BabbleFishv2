"""Factory for creating setup workflows"""

# maybe doesn't need to be factory prob one and done possibly
from typing import List

# imports
from src.providers import LLMProvider
from langgraph.graph import StateGraph, END, START
from src.core import Requirement
from . import LanguageDetector, StyleAnalyzer, GenreDetector
from src.workflows import SetupState


class SetupWorkflowFactory:
    """Factory for creating flexible setup workflows"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def create_workflow(self, requirements: List[Requirement]) -> StateGraph:
        workflow = StateGraph(SetupState)

        # adds needed nodes according to requirements
        nodes = {}
        for requirement in requirements:
            # matches auto break in python
            match requirement:
                case Requirement.STYLE_GUIDE:
                    nodes["style_analyzer"] = StyleAnalyzer(
                        self.llm_provider
                    ).analyze_style
                case Requirement.GENRES:
                    nodes["genre_detector"] = GenreDetector(
                        self.llm_provider
                    ).find_genres
                case Requirement.LANGUAGE:
                    nodes["language_detector"] = LanguageDetector().detect_language
                case _:
                    raise NotImplementedError(
                        f"The requirement {requirement.value} is not found"
                    )

        last_reference = START
        # Generates a simple path
        for reference, function in nodes.items():
            workflow.add_node(reference, function)
            workflow.add_edge(last_reference, reference)
            last_reference = reference
        workflow.add_edge(last_reference, END)

        return workflow.compile()
