"""Simple dependency injection container (manual implementation)."""

# type hints
from __future__ import annotations
from src.workflows import create_ingestion_workflow, create_translation_workflow
from src.knowledge_graph import KnowledgeGraphManager

# imports
from typing import Dict, Any
import asyncio
from src.providers import APIKeyManager, GoogleLLMProvider, MockLLMProvider
from src.knowledge_graph import KnowledgeGraphManager
from .schemas import AppConfig


class Container:
    """Simple dependency injection container for the application."""

    def __init__(self):
        """Initialize the container."""
        self._config: AppConfig = None
        self._instances: Dict[str, Any] = {}

    def set_config(self, config: AppConfig) -> None:
        """Set the application configuration.

        Args:
            config: The application configuration
        """
        self._config = config
        self._instances.clear()  # Clear existing instances when config changes

    def _get_api_key_manager(self) -> APIKeyManager:
        """Get or create the API key manager instance."""
        if "api_key_manager" not in self._instances:
            self._instances["api_key_manager"] = APIKeyManager(
                api_keys=self._config.llm.api_keys,
                max_usage_per_key=self._config.llm.max_requests_per_key,
            )
        return self._instances["api_key_manager"]

    def _get_llm_provider(self) -> GoogleLLMProvider:
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
            self._instances["kg_manager"] = KnowledgeGraphManager()
        return self._instances["kg_manager"]

    def _get_node_factory(workflow_type: str):
        workflow_types = {"translation", "ingestion"}
        if workflow_type not in workflow_types:
            raise NotImplementedError

    def get_translation_workflow(self):
        return create_translation_workflow(
            llm_provider=self._get_llm_provider(),
        )

    def get_ingestion_workflow(self):
        return create_ingestion_workflow(
            llm_provider=self._get_llm_provider(),
            kg_manager=self._get_knowledge_graph_manager(),
        )

    async def health_check(self) -> Dict[str, bool]:
        """Perform health checks on all components.

        Returns:
            Dictionary with health status of each component
        """
        results = {}

        try:
            llm_provider = self._get_llm_provider()
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
            llm_provider = self._get_llm_provider()
            if hasattr(llm_provider, "get_stats"):
                stats["llm_provider"] = await llm_provider.get_stats()
            else:
                stats["llm_provider"] = {
                    "available_keys": await llm_provider.get_available_keys_count()
                }
        except Exception as e:
            stats["llm_provider_error"] = str(e)

        return stats
