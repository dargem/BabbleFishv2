import os
import unittest

from src.nodes.ingestion.term_addition import term_addition_node
from tests.base import MockLLMTestCase
from tests.fixtures import CHINESE_SAMPLE_TEXT


class TestTermAdditionNode(MockLLMTestCase):
    """Test cases for NER"""

    def test_addition_node_returns_nodes(self):
        """Test that style node returns style_guide key."""
        self.mock_llm.invoke.return_value = MOCK_STYLE_GUIDE

        state = {"text": CHINESE_SAMPLE_TEXT}
        result = style_node(state)

        self.assert_state_has_key(result, "style_guide")
        self.assert_state_value_not_empty(result, "style_guide")
