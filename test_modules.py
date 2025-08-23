"""Simple test script to demonstrate individual module functionality."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.models import TranslationState
from src.nodes.language_detection import language_detector_node
from src.nodes.translation import translator_node
from src.config import config


def test_individual_nodes():
    """Test individual nodes in isolation."""

    # Test sample
    sample_text = "你好，世界！这是一个测试。"

    # Test language detection
    print("Testing Language Detection Node:")
    print("-" * 40)
    state = {"text": sample_text}
    result = language_detector_node(state)
    print(f"Input: {sample_text}")
    print(f"Detected Language: {result['language']}")

    # Test translation
    print("\nTesting Translation Node:")
    print("-" * 40)
    state.update(result)
    translation_result = translator_node(state)
    print(f"Translation: {translation_result['translation']}")

    print("\nConfiguration Test:")
    print("-" * 40)
    print(f"Model: {config.model_name}")
    print(f"Temperature: {config.temperature}")
    print(f"Max Feedback Loops: {config.max_feedback_loops}")


if __name__ == "__main__":
    test_individual_nodes()
