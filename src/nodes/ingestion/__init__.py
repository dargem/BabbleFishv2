""" Ingestion workflow nodes """

"""
Test on creating temporal knowledge graphs cooked up from this
https://cookbook.openai.com/examples/partners/temporal_agents_with_knowledge_graphs/temporal_agents_with_knowledge_graphs#2-how-to-use-this-cookbook
"""

from .triplet_extraction import entity_extractor_node
from .term_addition import term_addition_node

__all__ = [
    "entity_extractor_node",
    "term_addition_node",
]