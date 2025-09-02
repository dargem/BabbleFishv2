"""Interface for accessing the knowledge graph"""

from .graph_manager import KnowledgeGraphManager
from .query import KnowledgeGraphQuery
from .example_usage import example_usage
from .utils import (
    create_entity_from_dict,
    create_entity_from_neo4j_data,
    create_triplet_from_dict,
    merge_entity_names,
    find_entity_name_match,
    validate_triplet,
    group_entities_by_type,
    group_triplets_by_chapter,
    filter_triplets_by_confidence,
    get_entity_summary,
    get_triplet_summary,
    detect_potential_duplicates,
    get_name_translations_from_neo4j_data,
    print_entity_with_translations,
)

__all__ = [
    # Test usage temp
    "example_usage",
    # Core classes
    "KnowledgeGraphManager",
    "KnowledgeGraphQuery",
    # Utilities
    "create_entity_from_dict",
    "create_entity_from_neo4j_data",
    "create_triplet_from_dict",
    "merge_entity_names",
    "find_entity_name_match",
    "validate_triplet",
    "group_entities_by_type",
    "group_triplets_by_chapter",
    "filter_triplets_by_confidence",
    "get_entity_summary",
    "get_triplet_summary",
    "detect_potential_duplicates",
    "get_name_translations_from_neo4j_data",
    "print_entity_with_translations",
]
