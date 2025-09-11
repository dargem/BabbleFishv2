"""Environment-specific configuration loaders."""

import os
from abc import ABC, abstractmethod
from .schemas import AppConfig, DatabaseConfig, LLMConfig, WorkflowConfig


class ConfigLoader(ABC):
    """Abstract base class for environment-specific configuration loaders."""

    @abstractmethod
    def load(self) -> AppConfig:
        """Load configuration for this environment."""
        pass


class DevelopmentConfig(ConfigLoader):
    """Configuration for development environment."""

    def load(self) -> AppConfig:
        # Get API keys from environment
        api_keys = self._get_api_keys()

        return AppConfig(
            environment="development",
            debug=True,
            log_level="DEBUG",
            database=DatabaseConfig(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password=os.getenv("NEO4J_PASS"),
                connection_timeout=30,
            ),
            llm=LLMConfig(
                model_name="gemini-2.5-flash-lite",
                temperature=0.7,
                api_keys=api_keys,
                max_requests_per_key=15,
            ),
            workflow=WorkflowConfig(
                max_feedback_loops=3,
                enable_mermaid_graphs=True,
                chapter_processing_batch_size=5,
            ),
        )

    def _get_api_keys(self) -> list:
        """Extract API keys from environment variables."""
        keys = []

        # Look for numbered API keys (handle both uppercase and lowercase)
        for i in range(1, 21):  # Support up to 20 keys
            # Try uppercase first (standard)
            key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if not key:
                # Try lowercase as fallback
                key = os.getenv(f"google_api_key_{i}")
            if key:
                keys.append(key)

        # Also check for single key (both cases)
        single_key = os.getenv("GOOGLE_API_KEY") or os.getenv("google_api_key")
        if single_key and single_key not in keys:
            keys.append(single_key)

        if not keys:
            raise ValueError(
                "No Google API keys found. Set GOOGLE_API_KEY or GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, etc."
            )

        return keys


class ProductionConfig(ConfigLoader):
    """Configuration for production environment."""

    def load(self) -> AppConfig:
        api_keys = self._get_api_keys()

        return AppConfig(
            environment="production",
            debug=False,
            log_level="INFO",
            database=DatabaseConfig(
                neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
                neo4j_password=os.getenv(
                    "NEO4J_PASSWORD", "password"
                ),  # Provide default
                connection_timeout=60,
            ),
            llm=LLMConfig(
                model_name=os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash-lite"),
                temperature=float(
                    os.getenv("LLM_TEMPERATURE", "0.3")
                ),  # More deterministic
                api_keys=api_keys,
                max_requests_per_key=int(os.getenv("LLM_MAX_REQUESTS_PER_KEY", "15")),
            ),
            workflow=WorkflowConfig(
                max_feedback_loops=int(os.getenv("WORKFLOW_MAX_FEEDBACK_LOOPS", "5")),
                enable_mermaid_graphs=bool(
                    os.getenv("WORKFLOW_ENABLE_MERMAID", "false").lower() == "true"
                ),
                chapter_processing_batch_size=int(
                    os.getenv("WORKFLOW_BATCH_SIZE", "10")
                ),
            ),
        )

    def _get_api_keys(self) -> list:
        """Extract API keys from environment variables."""
        keys = []

        # Look for numbered API keys (handle both uppercase and lowercase)
        for i in range(1, 21):  # Support up to 20 keys in production
            # Try uppercase first (standard)
            key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if not key:
                # Try lowercase as fallback
                key = os.getenv(f"google_api_key_{i}")
            if key:
                keys.append(key)

        # Also check for single key (both cases)
        single_key = os.getenv("GOOGLE_API_KEY") or os.getenv("google_api_key")
        if single_key and single_key not in keys:
            keys.append(single_key)

        if not keys:
            raise ValueError("No Google API keys found in production environment")

        return keys


class TestingConfig(ConfigLoader):
    """Configuration for testing environment."""

    def load(self) -> AppConfig:
        return AppConfig(
            environment="testing",
            debug=True,
            log_level="WARNING",  # Reduce noise in tests
            database=DatabaseConfig(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="testing123",
                connection_timeout=5,
            ),
            llm=LLMConfig(
                model_name="gemini-2.5-flash-lite",
                temperature=0.0,  # Deterministic for tests
                api_keys=["test-api-key-1", "test-api-key-2"],  # Mock keys
                max_requests_per_key=5,
            ),
            workflow=WorkflowConfig(
                max_feedback_loops=2,
                enable_mermaid_graphs=False,  # Don't generate graphs in tests
                chapter_processing_batch_size=2,
            ),
        )


class ConfigFactory:
    """Factory for creating environment-specific configurations."""

    @staticmethod
    def create_config(env: str = None) -> AppConfig:
        """Create configuration for the specified environment.

        Args:
            env: Environment name ("development", "production", "testing")
                 If None, uses ENVIRONMENT env var or defaults to "development"

        Returns:
            AppConfig instance for the environment
        """
        if env is None:
            env = os.getenv("ENVIRONMENT", "development")

        loaders = {
            "development": DevelopmentConfig(),
            "production": ProductionConfig(),
            "testing": TestingConfig(),
        }

        if env not in loaders:
            raise ValueError(
                f"Unknown environment: {env}. Must be one of: {list(loaders.keys())}"
            )

        return loaders[env].load()
