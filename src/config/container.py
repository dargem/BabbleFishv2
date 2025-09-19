"""Simple dependency injection container (manual implementation)."""

# type hints
from __future__ import annotations
from typing import TYPE_CHECKING


# imports
from typing import Dict, Any
import asyncio
from src.providers import APIKeyManager, GoogleLLMProvider, MockLLMProvider
from src.workflows import IngestionWorkflowFactory, TranslationWorkflowFactory
from src.knowledge_graph import KnowledgeGraphManager, Neo4jConnection
from .schemas import AppConfig


class Container:
    """Simple dependency injection container for the application."""

    def __init__(self):
        """Initialize the container."""
        self._config: AppConfig = None
        self._instances: Dict[str, Any] = {}

    async def set_config(self, config: AppConfig) -> None:
        """Set the application configuration.

        Args:
            config: The application configuration
        """
        self._config = config
        self._instances.clear()  # Clear existing instances when config changes
        self._ingestion_workflow_factory = IngestionWorkflowFactory(
            self.get_llm_provider(),
            self._get_knowledge_graph_manager(),
        )
        stats = await self.get_stats()
        self._translation_workflow_factory = TranslationWorkflowFactory(
            self.get_llm_provider(),
            self._get_knowledge_graph_manager(),
            stats["config"]["max_feedback_loops"],
        )

    def _get_api_key_manager(self) -> APIKeyManager:
        """Get or create the API key manager instance."""
        if "api_key_manager" not in self._instances:
            self._instances["api_key_manager"] = APIKeyManager(
                api_keys=self._config.llm.api_keys,
                max_usage_per_key=self._config.llm.max_requests_per_key,
            )
        return self._instances["api_key_manager"]

    def get_llm_provider(self) -> GoogleLLMProvider:
        """Get or create the LLM provider instance."""
        provider_key = f"llm_provider_{self._config.environment}"

        if provider_key not in self._instances:
            if self._config.environment == "testing":
                # Use mock provider for testing
                self._instances[provider_key] = MockLLMProvider(
                    responses=[
                        "Mock translation",
                        "Mock feedback",
                        "approved response accepted",
                    ]
                )
            else:
                # Use real Google provider for dev/prod
                self._instances[provider_key] = GoogleLLMProvider(
                    api_key_manager=self._get_api_key_manager(),
                    model_name=self._config.llm.model_name,
                    temperature=self._config.llm.temperature,
                    max_tokens=self._config.llm.max_tokens,
                )

        return self._instances[provider_key]

    def _get_knowledge_graph_manager(self) -> KnowledgeGraphManager:
        """Get or create the knowledge graph manager instance."""
        if "kg_manager" not in self._instances:
            # Note: In the future, pass database config to KG manager
            connection = Neo4jConnection()
            self._instances["kg_manager"] = KnowledgeGraphManager(connection)
        return self._instances["kg_manager"]

    def get_translation_workflow(self):
        return self._translation_workflow_factory.create_workflow()

    def get_ingestion_workflow(self):
        return self._ingestion_workflow_factory.create_workflow()

    async def health_check(self) -> Dict[str, bool]:
        """Perform health checks on all components.

        Returns:
            Dictionary with health status of each component
        """
        results = {}

        try:
            llm_provider = self.get_llm_provider()
            results["llm_provider"] = await llm_provider.health_check()
        except Exception as e:
            results["llm_provider"] = False
            results["llm_provider_error"] = str(e)

        try:
            # Could add KG health check here
            results["knowledge_graph"] = True
        except Exception as e:
            results["knowledge_graph"] = False
            results["knowledge_graph_error"] = str(e)

        return results

    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics from all components.

        Returns:
            Dictionary with statistics from each component
        """
        stats = {
            "environment": self._config.environment,
            "config": {
                "llm_model": self._config.llm.model_name,
                "llm_temperature": self._config.llm.temperature,
                "max_feedback_loops": self._config.workflow.max_feedback_loops,
            },
        }

        try:
            llm_provider = self.get_llm_provider()
            if hasattr(llm_provider, "get_stats"):
                stats["llm_provider"] = await llm_provider.get_stats()
            else:
                stats["llm_provider"] = {
                    "available_keys": await llm_provider.get_available_keys_count()
                }
        except Exception as e:
            stats["llm_provider_error"] = str(e)

        return stats


from typing import Any, Dict, Callable
from src.providers import APIKeyManager, GoogleLLMProvider, MockLLMProvider
from src.workflows import IngestionWorkflowFactory, TranslationWorkflowFactory
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

    def get(self, key: Any):
        """Generic resolver with caching."""
        if key in self._instances:
            return self._instances[key]
        if key not in self._providers:
            raise ValueError(f"No provider registered for {key}")
        instance = self._providers[key](self)
        self._instances[key] = instance
        return instance

    def get_ingestion_workflow(self):
        return self.get(IngestionWorkflowFactory).create_workflow()

    def get_translation_workflow(self):
        return self.get(TranslationWorkflowFactory).create_workflow()

    async def health_check(self):
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
