"""Interface for accessing the knowledge graph"""

from .models import Entity, Triplet, EntityType, TripletMetadata
from .graph_manager import KnowledgeGraphManager
from .query import KnowledgeGraphQuery
from .utils import (
    create_entity_from_dict,
    create_triplet_from_dict,
    merge_entity_names,
    find_entity_name_match,
    validate_triplet,
    group_entities_by_type,
    group_triplets_by_chapter,
    filter_triplets_by_confidence,
    get_entity_summary,
    get_triplet_summary,
    detect_potential_duplicates
)

__all__ = [
    # Models
    "Entity",
    "Triplet", 
    "EntityType",
    "TripletMetadata",
    # Core classes
    "KnowledgeGraphManager",
    "KnowledgeGraphQuery",
    # Utilities
    "create_entity_from_dict",
    "create_triplet_from_dict",
    "merge_entity_names",
    "find_entity_name_match",
    "validate_triplet",
    "group_entities_by_type",
    "group_triplets_by_chapter",
    "filter_triplets_by_confidence",
    "get_entity_summary",
    "get_triplet_summary",
    "detect_potential_duplicates"
]
