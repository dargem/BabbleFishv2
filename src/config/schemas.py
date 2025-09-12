"""Configuration schemas with validation."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class DatabaseConfig(BaseModel):
    """Configuration for Neo4j database connection."""

    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="password")
    connection_timeout: int = Field(default=30)

    model_config = {"extra": "forbid"}


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""

    model_name: str = Field(default="gemini-2.5-flash-lite")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None)
    api_keys: List[str] = Field(min_items=1)
    max_requests_per_key: int = Field(default=15, ge=1, le=100)

    @field_validator("api_keys")
    def validate_api_keys(cls, v):
        if not v or any(not key.strip() for key in v):
            raise ValueError("All API keys must be non-empty")
        return [key.strip() for key in v]

    @field_validator("model_name")
    def validate_model_name(cls, v):
        allowed_models = [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
        ]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of: {allowed_models}")
        return v

    model_config = {"extra": "forbid"}


class WorkflowConfig(BaseModel):
    """Configuration for workflow behavior."""

    max_feedback_loops: int = Field(default=3, ge=1, le=10)
    enable_mermaid_graphs: bool = Field(default=True)
    chapter_processing_batch_size: int = Field(default=5, ge=1, le=50)

    model_config = {"extra": "forbid"}


class AppConfig(BaseModel):
    """Main application configuration."""

    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Nested configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)

    @field_validator("log_level")
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    model_config = {"extra": "forbid"}
