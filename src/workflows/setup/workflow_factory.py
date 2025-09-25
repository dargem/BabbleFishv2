"""Factory for creating setup workflows"""

# maybe doesn't need to be factory prob one and done possibly
from typing import List

# imports
from src.providers import LLMProvider
from langgraph.graph import StateGraph, END, START
from ..states import SetupState
from src.core import Requirement


class SetupWorkflowFactory:
    """Factory for creating flexible setup workflows"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def create_workflow(
        self, requirements: List[Requirement]
    ) -> StateGraph:
        nodes = []

        for requirement in requirement:
            # matches auto break in python
            match requirement:
                case Requirement.STYLE_GUIDE:
                    pass
                case Requirement.GENRES:
                    pass
                case Requirement.LANGUAGE:
                    pass
                case _:
                    raise NotImplementedError(
                        f"The requirement {requirement.value} is not found"
                    )
