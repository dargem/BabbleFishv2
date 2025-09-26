"""Simple dependency injection container"""

from typing import Any, Dict, Callable
from src.providers import APIKeyManager, GoogleLLMProvider, MockLLMProvider
from src.workflows import (
    IngestionWorkflowFactory,
    TranslationWorkflowFactory,
    SetupWorkflowFactory,
)
from src.knowledge_graph import KnowledgeGraphManager, Neo4jConnection
from .schemas import AppConfig


class Container:
    """Dependency injection container using a registry of providers."""

    def __init__(self):
        self._config: AppConfig | None = None
        self._instances: Dict[Any, Any] = {}
        self._providers: Dict[Any, Callable[["Container"], Any]] = {}

    async def set_config(self, config: AppConfig) -> None:
        """Set the app config and register providers."""
        self._config = config
        self._instances.clear()
        self._providers.clear()

        # Registry providers
        self._providers[APIKeyManager] = lambda c: APIKeyManager(
            api_keys=config.llm.api_keys,
            max_usage_per_key=config.llm.max_requests_per_key,
        )

        self._providers[GoogleLLMProvider] = lambda c: GoogleLLMProvider(
            api_key_manager=c.get(APIKeyManager),
            model_name=config.llm.model_name,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )

        self._providers[MockLLMProvider] = lambda c: MockLLMProvider(
            responses=[
                "Mock translation",
                "Mock feedback",
                "approved response accepted",
            ]
        )

        self._providers[KnowledgeGraphManager] = lambda c: KnowledgeGraphManager(
            Neo4jConnection()
        )

        # Factories depend on stats needs KG calls
        stats = await self.get_stats()

        self._providers[IngestionWorkflowFactory] = lambda c: IngestionWorkflowFactory(
            c.get(GoogleLLMProvider)
            if config.environment != "testing"
            else c.get(MockLLMProvider),
            c.get(KnowledgeGraphManager),
        )

        self._providers[TranslationWorkflowFactory] = (
            lambda c: TranslationWorkflowFactory(
                c.get(GoogleLLMProvider)
                if config.environment != "testing"
                else c.get(MockLLMProvider),
                c.get(KnowledgeGraphManager),
                stats["config"]["max_feedback_loops"],
            )
        )

        self._providers[SetupWorkflowFactory] = lambda c: SetupWorkflowFactory(
            c.get(GoogleLLMProvider)
            if config.environment != "testing"
            else c.get(MockLLMProvider),
        )

        # Register NovelTranslator with proper dependency injection
        from src.translation_orchestration.novel_processor import NovelTranslator

        self._providers[NovelTranslator] = lambda c: NovelTranslator(
            setup_workflow_factory=c.get(SetupWorkflowFactory),
            ingestion_workflow_factory=c.get(IngestionWorkflowFactory),
            translation_workflow_factory=c.get(TranslationWorkflowFactory),
        )

        # Register WorkflowRegistry with proper dependency injection
        from src.translation_orchestration.workflow_registry import WorkflowRegistry

        self._providers[WorkflowRegistry] = lambda c: WorkflowRegistry(
            setup_factory=c.get(SetupWorkflowFactory),
            ingestion_factory=c.get(IngestionWorkflowFactory),
            translation_factory=c.get(TranslationWorkflowFactory),
        )

    def get(self, key: Any):
        """
        Generic resolver with caching

        Args:
            key: The requested class

        Returns:
            An initialized object of key (the requested class)
        """

        if key in self._instances:
            return self._instances[key]
        if key not in self._providers:
            raise ValueError(f"No provider registered for {key}")
        instance = self._providers[key](self)
        self._instances[key] = instance
        return instance

    def get_setup_workflow(self, requirements):
        return self.get(SetupWorkflowFactory).create_workflow(requirements)

    def get_ingestion_workflow(self):
        return self.get(IngestionWorkflowFactory).create_workflow()

    def get_translation_workflow(self):
        return self.get(TranslationWorkflowFactory).create_workflow()

    def get_novel_translator(self, novel=None):
        """Get a NovelTranslator instance with optional novel"""
        from src.translation_orchestration.novel_processor import NovelTranslator

        translator = self.get(NovelTranslator)
        if novel:
            translator.novel = novel
        return translator

    async def health_check(self):
        """
        Checks for expired API keys and if the database is working

        Returns:
            Dict of test result
        """
        results = {}
        try:
            provider = self.get(
                MockLLMProvider
                if self._config.environment == "testing"
                else GoogleLLMProvider
            )
            results["llm_provider"] = await provider.health_check()
        except Exception as e:
            results["llm_provider"] = False
            results["llm_provider_error"] = str(e)

        try:
            kg: KnowledgeGraphManager = self.get(KnowledgeGraphManager)
            # send a query, if connection fails it will crash not hang
            kg.get_stats()
            results["knowledge_graph"] = True
        except Exception as e:
            results["knowledge_graph"] = False
            results["knowledge_graph_error"] = str(e)

        return results

    async def get_stats(self):
        stats = {
            "environment": self._config.environment,
            "config": {
                "llm_model": self._config.llm.model_name,
                "llm_temperature": self._config.llm.temperature,
                "max_feedback_loops": self._config.workflow.max_feedback_loops,
            },
        }

        try:
            provider = self.get(
                MockLLMProvider
                if self._config.environment == "testing"
                else GoogleLLMProvider
            )
            if hasattr(provider, "get_stats"):
                stats["llm_provider"] = await provider.get_stats()
            else:
                stats["llm_provider"] = {
                    "available_keys": await provider.get_available_keys_count()
                }
        except Exception as e:
            stats["llm_provider_error"] = str(e)

        return stats
