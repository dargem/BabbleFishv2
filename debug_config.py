#!/usr/bin/env python3
"""Debug script to test configuration loading."""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from src.config import ConfigFactory

    print("Testing configuration loading...")

    # Test each environment
    for env in ["development", "testing", "production"]:
        print(f"\n--- Testing {env} environment ---")
        try:
            config = ConfigFactory.create_config(env=env)
            print(f"✓ {env} config loaded successfully")
            print(f"  Environment: {config.environment}")
            print(f"  Neo4j URI: {config.database.neo4j_uri}")
            print(f"  LLM Model: {config.llm.model_name}")
            print(f"  API Keys: {len(config.llm.api_keys)} keys")
        except Exception as e:
            print(f"✗ {env} config failed: {e}")
            import traceback

            traceback.print_exc()

except ImportError as e:
    print(f"Import error: {e}")
    print(
        "Make sure you're running from the project root and have installed dependencies"
    )
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
