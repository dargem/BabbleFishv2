"""
Legacy interface for knowledge graph operations.
This file is kept for compatibility but the new interface should be used instead.
"""

import warnings
from .graph_manager import KnowledgeGraphManager
from .models import Entity, EntityType

# Deprecation warning
warnings.warn(
    "The addition.py interface is deprecated. Please use KnowledgeGraphManager directly.",
    DeprecationWarning,
    stacklevel=2
)

# Global manager instance for legacy compatibility
_global_manager = None

def get_manager():
    """Get or create the global manager instance"""
    global _global_manager
    if _global_manager is None:
        _global_manager = KnowledgeGraphManager()
    return _global_manager


def add_entities(entities):
    """Legacy function - use KnowledgeGraphManager.add_entities() instead"""
    return get_manager().add_entities(entities)


def get_entities():
    """Legacy function - use KnowledgeGraphManager.get_all_entities() instead"""
    return get_manager().get_all_entities()


def reset_database():
    """Legacy function - use KnowledgeGraphManager.reset_database() instead"""
    return get_manager().reset_database()


def close_connection():
    """Close the global manager connection"""
    global _global_manager
    if _global_manager:
        _global_manager.close()
        _global_manager = None

