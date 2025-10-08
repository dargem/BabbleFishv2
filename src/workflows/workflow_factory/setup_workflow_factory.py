"""Factory for creating setup workflows"""

# imports
from src.providers import LLMProvider, NLPProvider
from langgraph.graph import StateGraph, END, START
from ..setup_nodes import LanguageDetector, StyleAnalyzer, GenreDetector, Tagger
from src.workflows import SetupState
from . import AbstractWorkflowFactory


class SetupWorkflowFactory(AbstractWorkflowFactory):
    """Factory for creating setup workflows that perform all setup tasks"""

    def __init__(self, llm_provider: LLMProvider, nlp_provider: NLPProvider):
        self.llm_provider = llm_provider
        self.nlp_provider = nlp_provider

    def create_workflow(self) -> StateGraph:
        """
        Create a complete setup workflow that analyzes language, style, and genres

        Returns:
            Compiled setup workflow that performs all setup requirements
        """
        workflow = StateGraph(SetupState)

        # Create all setup nodes
        language_detector = LanguageDetector()
        style_analyzer = StyleAnalyzer(self.llm_provider)
        genre_detector = GenreDetector(self.llm_provider)
        tagger = Tagger(self.llm_provider, self.nlp_provider)

        # Add nodes
        workflow.add_node("language_detector", language_detector.detect_language)
        workflow.add_node("style_analyzer", style_analyzer.analyze_style)
        workflow.add_node("genre_detector", genre_detector.find_genres)
        workflow.add_node("tagger", tagger.tag_content)

        # Add routing
        workflow.add_edge(START, "language_detector")
        workflow.add_edge("language_detector", "style_analyzer")
        workflow.add_edge("style_analyzer", "genre_detector")
        workflow.add_edge("genre_detector", "tagger")
        workflow.add_edge("tagger", END)

        return workflow.compile()
