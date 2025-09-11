"""Mock LLM provider for testing."""

import asyncio
from typing import List
import logging
from langchain.schema import BaseMessage

from .base import LLMProvider


logger = logging.getLogger(__name__)


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing purposes."""
    
    def __init__(self, responses: List[str] = None, should_fail: bool = False, 
                 fail_after: int = None):
        """Initialize the mock LLM provider.
        
        Args:
            responses: List of canned responses to cycle through
            should_fail: Whether to always fail requests
            fail_after: Fail after this many successful requests
        """
        self.responses = responses or ["Mock response"]
        self.should_fail = should_fail
        self.fail_after = fail_after
        self.request_count = 0
        self.is_healthy = True
    
    async def invoke(self, messages: List[BaseMessage]) -> str:
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
        
        logger.debug(f"Mock LLM returning response {response_index + 1}: {response[:50]}...")
        return response
    
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