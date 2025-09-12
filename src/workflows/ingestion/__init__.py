"""Ingestion workflow nodes"""

"""
Test on creating temporal knowledge graphs cooked up from this
https://cookbook.openai.com/examples/partners/temporal_agents_with_knowledge_graphs/temporal_agents_with_knowledge_graphs#2-how-to-use-this-cookbook
"""


from .triplet_extraction import triplet_extractor_node
from .term_addition import EntityCreator

__all__ = [
    "triplet_extractor_node",
    "EntityCreator",
]
