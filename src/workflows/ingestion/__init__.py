"""Ingestion workflow nodes"""

"""
Test on creating temporal knowledge graphs cooked up from this
https://cookbook.openai.com/examples/partners/temporal_agents_with_knowledge_graphs/temporal_agents_with_knowledge_graphs#2-how-to-use-this-cookbook
"""


from .triplet_creator import TripletCreator
from .term_creator import EntityCreator

__all__ = [
    "TripletCreator",
    "EntityCreator",
]
