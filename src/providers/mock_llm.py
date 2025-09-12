"""Mock LLM provider for testing."""

import asyncio
from typing import List
import logging
from langchain.schema import BaseMessage
from pydantic import BaseModel
from .base import LLMProvider


logger = logging.getLogger(__name__)


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing purposes."""

    def __init__(
        self,
        responses: List[str] = None,
        should_fail: bool = False,
        fail_after: int = None,
        structured_responses: dict = None,
    ):
        """Initialize the mock LLM provider.

        Args:
            responses: List of canned responses to cycle through
            should_fail: Whether to always fail requests
            fail_after: Fail after this many successful requests
            structured_responses: Dict mapping schema class names to response instances
        """
        self.responses = responses or ["Mock response"]
        self.should_fail = should_fail
        self.fail_after = fail_after
        self.structured_responses = structured_responses or {}
        self.request_count = 0
        self.is_healthy = True

    async def invoke(self, message: List[BaseMessage]) -> str:
        """Mock LLM invocation.

        Args:
            messages: List of messages (ignored in mock)

        Returns:
            A canned response or raises an exception

        Raises:
            Exception: If configured to fail
        """
        self.request_count += 1

        # Simulate network delay
        await asyncio.sleep(0.1)

        # Check if we should fail
        if self.should_fail:
            raise Exception("Mock LLM configured to fail")

        if self.fail_after and self.request_count > self.fail_after:
            raise Exception(f"Mock LLM failed after {self.fail_after} requests")

        # Return a canned response
        response_index = (self.request_count - 1) % len(self.responses)
        response = self.responses[response_index]

        logger.debug(
            f"Mock LLM returning response {response_index + 1}: {response[:50]}..."
        )
        return response

    async def schema_invoke(
        self, messages: List[BaseMessage], schema: BaseModel
    ) -> BaseModel:
        """Mock LLM invocation with structured output.

        Args:
            messages: List of messages (ignored in mock)
            schema: BaseModel schema for structured response

        Returns:
            A mock instance of the specified schema

        Raises:
            Exception: If configured to fail
        """
        self.request_count += 1

        # Simulate network delay
        await asyncio.sleep(0.1)

        if self.should_fail:
            raise Exception("Mock LLM configured to fail")

        if self.fail_after and self.request_count > self.fail_after:
            raise Exception(f"Mock LLM failed after {self.fail_after} requests")

        # Create a mock instance of the schema with default values
        schema_name = schema.__name__

        # Check if we have a pre-configured response for this schema
        if schema_name in self.structured_responses:
            response = self.structured_responses[schema_name]
            logger.debug(
                f"Mock LLM returning pre-configured structured response for schema: {schema_name}"
            )
            return response

        try:
            # Try to create instance with minimal valid data
            mock_instance = schema()
            logger.debug(
                f"Mock LLM returning default structured response for schema: {schema_name}"
            )
            return mock_instance
        except Exception as e:
            # If schema requires specific fields, create with mock data
            logger.warning(f"Could not create default schema instance: {e}")
            # For now, raise an exception - in a real implementation you might
            # want to intelligently populate required fields based on schema
            raise Exception(
                f"Mock LLM cannot create instance of schema {schema_name}: {e}"
            )

    async def health_check(self) -> bool:
        """Mock health check.

        Returns:
            True if healthy, False otherwise
        """
        return self.is_healthy and not self.should_fail

    async def get_available_keys_count(self) -> int:
        """Mock available keys count.

        Returns:
            Always returns 1 for mock provider
        """
        return 1 if self.is_healthy else 0

    def set_responses(self, responses: List[str]) -> None:
        """Update the list of canned responses.

        Args:
            responses: New list of responses
        """
        self.responses = responses

    def set_structured_response(self, schema: BaseModel, response: BaseModel) -> None:
        """Set a specific structured response for a schema.

        Args:
            schema: The schema class to set response for
            response: The response instance to return for this schema
        """
        self.structured_responses[schema.__name__] = response

    def set_structured_responses(self, responses: dict) -> None:
        """Update the structured responses mapping.

        Args:
            responses: Dict mapping schema class names to response instances
        """
        self.structured_responses = responses

    def set_health(self, is_healthy: bool) -> None:
        """Set the health status of the mock provider.

        Args:
            is_healthy: Whether the provider should be healthy
        """
        self.is_healthy = is_healthy

    def reset(self) -> None:
        """Reset the mock provider state."""
        self.request_count = 0
        self.is_healthy = True
        self.should_fail = False
        self.structured_responses = {}
