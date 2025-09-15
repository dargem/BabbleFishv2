"""Example of how to use the new provider architecture."""

import asyncio
from langchain.schema import HumanMessage

from src.config import ConfigFactory, Container
from src.providers import LLMProvider


async def example_basic_usage():
    """Basic example of using the new provider architecture."""
    print("=== Basic Provider Usage Example ===")

    # Load configuration for development environment
    config = ConfigFactory.create_config(env="development")

    # Create and configure container
    container = Container()
    container.set_config(config)

    # Get LLM provider (automatically handles key rotation)
    llm_provider: LLMProvider = container.get_llm_provider()

    # Use the provider for translation
    messages = [HumanMessage(content="Translate this to English: Bonjour le monde")]

    try:
        response = await llm_provider.invoke(messages)
        print(f"Translation response: {response}")
    except Exception as e:
        print(f"Translation failed: {e}")

    # Check provider health
    is_healthy = await llm_provider.health_check()
    print(f"Provider healthy: {is_healthy}")

    # Get available keys count
    key_count = await llm_provider.get_available_keys_count()
    print(f"Available keys: {key_count}")


async def example_multiple_requests():
    """Example showing automatic key rotation across multiple requests."""
    print("\n=== Multiple Requests Example ===")

    config = ConfigFactory.create_config(env="development")
    container = Container()
    container.set_config(config)

    llm_provider = container.get_llm_provider()

    # Make multiple requests to trigger key rotation
    for i in range(5):
        try:
            messages = [HumanMessage(content=f"Translate #{i + 1}: Hello world")]
            response = await llm_provider.invoke(messages)
            print(f"Request {i + 1}: {response[:50]}...")
        except Exception as e:
            print(f"Request {i + 1} failed: {e}")

        # Small delay between requests
        await asyncio.sleep(0.5)


async def example_testing_environment():
    """Example using the testing environment with mock provider."""
    print("\n=== Testing Environment Example ===")

    # Load testing config (uses mock provider)
    config = ConfigFactory.create_config(env="testing")
    container = Container()
    container.set_config(config)

    llm_provider = container.get_llm_provider()

    # This will use the mock provider
    messages = [HumanMessage(content="This will be mocked")]
    response = await llm_provider.invoke(messages)
    print(f"Mock response: {response}")


async def example_health_monitoring():
    """Example of health monitoring and statistics."""
    print("\n=== Health Monitoring Example ===")

    config = ConfigFactory.create_config(env="development")
    container = Container()
    container.set_config(config)

    # Perform health check on all components
    health_status = await container.health_check()
    print("Health Status:")
    for component, status in health_status.items():
        print(f"  {component}: {'✓' if status else '✗'}")

    # Get detailed statistics
    stats = await container.get_stats()
    print("\nSystem Statistics:")
    print(f"  Environment: {stats['environment']}")
    print(f"  LLM Model: {stats['config']['llm_model']}")
    print(f"  Temperature: {stats['config']['llm_temperature']}")

    if "llm_provider" in stats and "api_keys" in stats["llm_provider"]:
        print("  API Key Status:")
        for key_suffix, key_stats in stats["llm_provider"]["api_keys"].items():
            print(
                f"    {key_suffix}: {key_stats['usage_count']} requests, "
                f"healthy: {key_stats['is_healthy']}"
            )


async def example_workflow_integration():
    """Example of how this integrates with your existing workflows."""
    print("\n=== Workflow Integration Example ===")

    config = ConfigFactory.create_config(env="development")
    container = Container()
    container.set_config(config)

    # Get dependencies
    llm_provider = container.get_llm_provider()
    kg_manager = container._get_knowledge_graph_manager()

    # This is how your workflow nodes would now work:
    class ModernTranslatorNode:
        def __init__(self, llm_provider: LLMProvider):
            self.llm_provider = llm_provider

        async def translate(self, text: str) -> str:
            messages = [HumanMessage(content=f"Translate to English: {text}")]
            return await self.llm_provider.invoke(messages)

    # Create and use the node
    translator = ModernTranslatorNode(llm_provider)
    result = await translator.translate("Bonjour")
    print(f"Modern translator result: {result}")

    print("\nKey benefits:")
    print("  ✓ Automatic API key rotation")
    print("  ✓ Health checking and error recovery")
    print("  ✓ Easy to test (inject mock provider)")
    print("  ✓ Environment-specific configuration")
    print("  ✓ Loose coupling between components")


async def main():
    """Run all examples."""
    await example_basic_usage()
    await example_multiple_requests()
    await example_testing_environment()
    await example_health_monitoring()
    await example_workflow_integration()


if __name__ == "__main__":
    print("BabbleFish v2 - New Provider Architecture Examples")
    print("=" * 50)
    asyncio.run(main())
