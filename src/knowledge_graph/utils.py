"""Utilities for knowledge graph operations"""

from typing import List, Dict, Any, Tuple, Optional
from .models import Entity, Triplet, EntityType, TripletMetadata


def create_entity_from_dict(data: Dict[str, Any]) -> Entity:
    """
    Create an Entity object from a dictionary
    
    Args:
        data: Dictionary containing entity data
        
    Returns:
        Entity object
    """
    entity_type = EntityType(data.get("entity_type", "Concept"))
    
    return Entity(
        names=data.get("names", []),
        entity_type=entity_type,
        translation=data.get("translation"),
        description=data.get("description"),
        chapter_idx=data.get("chapter_idx"),
        properties=data.get("properties", {})
    )


def create_triplet_from_dict(data: Dict[str, Any]) -> Triplet:
    """
    Create a Triplet object from a dictionary
    
    Args:
        data: Dictionary containing triplet data
        
    Returns:
        Triplet object
    """
    metadata_dict = data.get("metadata", {})
    
    metadata = TripletMetadata(
        chapter_idx=metadata_dict.get("chapter_idx", 0),
        temporal_type=metadata_dict.get("temporal_type"),
        statement_type=metadata_dict.get("statement_type"),
        confidence=metadata_dict.get("confidence"),
        source_text=metadata_dict.get("source_text"),
        additional_props=metadata_dict.get("additional_props", {})
    )
    
    return Triplet(
        subject_name=data["subject_name"],
        predicate=data["predicate"],
        object_name=data["object_name"],
        metadata=metadata
    )


def merge_entity_names(existing_names: List[str], new_names: List[str]) -> List[str]:
    """
    Merge entity names, avoiding duplicates
    
    Args:
        existing_names: Current entity names
        new_names: New names to add
        
    Returns:
        Merged list of unique names
    """
    # Convert to sets for efficient operations
    existing_set = set(name.lower() for name in existing_names)
    merged_names = existing_names.copy()
    
    for new_name in new_names:
        if new_name.lower() not in existing_set:
            merged_names.append(new_name)
            existing_set.add(new_name.lower())
    
    return merged_names


def find_entity_name_match(target_name: str, entity_names: List[str]) -> Optional[str]:
    """
    Find if a target name matches any entity names (case-insensitive)
    
    Args:
        target_name: Name to search for
        entity_names: List of entity names to search in
        
    Returns:
        Matching name if found, None otherwise
    """
    target_lower = target_name.lower()
    for name in entity_names:
        if name.lower() == target_lower:
            return name
    return None


def validate_triplet(triplet: Triplet, available_entities: List[Entity]) -> Tuple[bool, str]:
    """
    Validate that a triplet's subject and object entities exist
    
    Args:
        triplet: Triplet to validate
        available_entities: List of available entities
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    entity_names = set()
    for entity in available_entities:
        entity_names.update(name.lower() for name in entity.names)
    
    subject_found = triplet.subject_name.lower() in entity_names
    object_found = triplet.object_name.lower() in entity_names
    
    if not subject_found and not object_found:
        return False, f"Neither subject '{triplet.subject_name}' nor object '{triplet.object_name}' found"
    elif not subject_found:
        return False, f"Subject entity '{triplet.subject_name}' not found"
    elif not object_found:
        return False, f"Object entity '{triplet.object_name}' not found"
    
    return True, ""


def group_entities_by_type(entities: List[Entity]) -> Dict[EntityType, List[Entity]]:
    """
    Group entities by their type
    
    Args:
        entities: List of entities to group
        
    Returns:
        Dictionary mapping entity types to lists of entities
    """
    grouped = {}
    for entity in entities:
        if entity.entity_type not in grouped:
            grouped[entity.entity_type] = []
        grouped[entity.entity_type].append(entity)
    
    return grouped


def group_triplets_by_chapter(triplets: List[Triplet]) -> Dict[int, List[Triplet]]:
    """
    Group triplets by chapter
    
    Args:
        triplets: List of triplets to group
        
    Returns:
        Dictionary mapping chapter indices to lists of triplets
    """
    grouped = {}
    for triplet in triplets:
        chapter = triplet.metadata.chapter_idx
        if chapter not in grouped:
            grouped[chapter] = []
        grouped[chapter].append(triplet)
    
    return grouped


def filter_triplets_by_confidence(triplets: List[Triplet], min_confidence: float) -> List[Triplet]:
    """
    Filter triplets by minimum confidence threshold
    
    Args:
        triplets: List of triplets to filter
        min_confidence: Minimum confidence score (0-1)
        
    Returns:
        Filtered list of triplets
    """
    return [
        triplet for triplet in triplets
        if triplet.metadata.confidence is not None and triplet.metadata.confidence >= min_confidence
    ]


def get_entity_summary(entity: Entity) -> str:
    """
    Generate a human-readable summary of an entity
    
    Args:
        entity: Entity to summarize
        
    Returns:
        Summary string
    """
    names_str = ", ".join(entity.names)
    summary = f"{entity.entity_type.value}: {names_str}"
    
    if entity.description:
        summary += f" - {entity.description}"
    
    if entity.chapter_idx is not None:
        summary += f" (Chapter {entity.chapter_idx})"
    
    return summary


def get_triplet_summary(triplet: Triplet) -> str:
    """
    Generate a human-readable summary of a triplet
    
    Args:
        triplet: Triplet to summarize
        
    Returns:
        Summary string
    """
    summary = f"{triplet.subject_name} -[{triplet.predicate}]-> {triplet.object_name}"
    
    if triplet.metadata.chapter_idx:
        summary += f" (Chapter {triplet.metadata.chapter_idx})"
    
    if triplet.metadata.temporal_type:
        summary += f" [{triplet.metadata.temporal_type}]"
    
    if triplet.metadata.statement_type:
        summary += f" ({triplet.metadata.statement_type})"
    
    return summary


def detect_potential_duplicates(entities: List[Entity], similarity_threshold: float = 0.8) -> List[Tuple[Entity, Entity, float]]:
    """
    Detect potential duplicate entities based on name similarity
    
    Args:
        entities: List of entities to check
        similarity_threshold: Similarity threshold for detecting duplicates
        
    Returns:
        List of tuples containing (entity1, entity2, similarity_score)
    """
    # This is a simple implementation - in practice you might want to use
    # more sophisticated similarity algorithms
    duplicates = []
    
    for i, entity1 in enumerate(entities):
        for j, entity2 in enumerate(entities[i+1:], i+1):
            max_similarity = 0.0
            
            # Check similarity between all name combinations
            for name1 in entity1.names:
                for name2 in entity2.names:
                    # Simple Jaccard similarity based on character n-grams
                    similarity = _calculate_simple_similarity(name1.lower(), name2.lower())
                    max_similarity = max(max_similarity, similarity)
            
            if max_similarity >= similarity_threshold:
                duplicates.append((entity1, entity2, max_similarity))
    
    return duplicates


def _calculate_simple_similarity(str1: str, str2: str) -> float:
    """
    Calculate simple similarity between two strings using character bigrams
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Similarity score between 0 and 1
    """
    if str1 == str2:
        return 1.0
    
    # Create character bigrams
    bigrams1 = set(str1[i:i+2] for i in range(len(str1)-1))
    bigrams2 = set(str2[i:i+2] for i in range(len(str2)-1))
    
    if not bigrams1 and not bigrams2:
        return 1.0
    if not bigrams1 or not bigrams2:
        return 0.0
    
    # Jaccard similarity
    intersection = len(bigrams1.intersection(bigrams2))
    union = len(bigrams1.union(bigrams2))
    
    return intersection / union if union > 0 else 0.0
