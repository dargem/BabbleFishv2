"""Utilities for knowledge graph operations"""

from typing import List, Dict, Any, Tuple, Optional
from src.core import (
    Entity,
    InputTriplet,
    EntityType,
    TripletMetadata,
    NameEntry,
    Direction
)


def create_entity_from_neo4j_data(data: Dict[str, Any]) -> Entity:
    """
    Create an Entity object from Neo4j data

    Args:
        data: Dictionary containing Neo4j node properties

    Returns:
        Entity object
    """
    entity_type = EntityType(data.get("entity_type", "CONCEPT"))

    # Handle the new parallel arrays format
    if "names_list" in data and data["names_list"]:
        names_list = data["names_list"]
        translations_list = data.get("translations_list", [""] * len(names_list))
        is_weak_list = data.get("is_weak_list", [False] * len(names_list))

        # Ensure all lists are the same length
        max_len = len(names_list)
        if len(translations_list) < max_len:
            translations_list.extend([""] * (max_len - len(translations_list)))
        if len(is_weak_list) < max_len:
            is_weak_list.extend([False] * (max_len - len(is_weak_list)))

        names = [
            NameEntry(
                name=names_list[i],
                translation=translations_list[i],
                is_weak=is_weak_list[i],
            )
            for i in range(max_len)
        ]
    # Fallback to all_names if new format doesn't exist
    elif "all_names" in data:
        names = [
            NameEntry(name=name, translation="", is_weak=False)
            for name in data["all_names"]
        ]
    else:
        names = []

    return Entity(
        names=names,
        entity_type=entity_type,
        description=data.get("description", ""),
        chapter_idx=data.get("chapter_idx", []),
        properties={
            k: v
            for k, v in data.items()
            if k
            not in [
                "names_list",
                "translations_list",
                "is_weak_list",
                "all_names",
                "entity_type",
                "description",
                "chapter_idx",
                "strong_names",
                "weak_names",
            ]
        },
    )


def get_name_translations_from_neo4j_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract name-to-translation mapping from Neo4j node data

    Args:
        data: Neo4j node properties

    Returns:
        Dictionary mapping names to translations
    """
    if "names_list" in data and "translations_list" in data:
        names_list = data["names_list"]
        translations_list = data.get("translations_list", [])

        # Create mapping, handling cases where lists might be different lengths
        translations = {}
        for i, name in enumerate(names_list):
            if i < len(translations_list) and translations_list[i]:
                translations[name] = translations_list[i]
            else:
                translations[name] = ""  # Default to empty if no translation

        return translations
    return {}


def print_entity_with_translations(entity: Entity) -> None:
    """
    Print an entity with all its name-translation pairs

    Args:
        entity: Entity to print
    """
    print(f"\n{entity.entity_type.value}: {entity.description}")
    print("Names and translations:")
    for name_entry in entity.names:
        status = "weak" if name_entry.is_weak else "strong"
        print(f"  '{name_entry.name}' → '{name_entry.translation}' ({status})")

    if entity.chapter_idx:
        chapters = ", ".join(map(str, entity.chapter_idx))
        print(f"Appears in chapters: {chapters}")


def create_entity_from_dict(data: Dict[str, Any]) -> Entity:
    """
    Create an Entity object from a dictionary

    Args:
        data: Dictionary containing entity data

    Returns:
        Entity object
    """
    entity_type = EntityType(data.get("entity_type", "CONCEPT"))

    # Handle both old format (list of strings) and new format (list of NameEntry data)
    names_data = data.get("names", [])
    if names_data and isinstance(names_data[0], dict):
        # New format with NameEntry data
        names = [
            NameEntry(
                name=entry["name"],
                translation=entry.get("translation", ""),
                is_weak=entry.get("is_weak", False),
            )
            for entry in names_data
        ]
    elif names_data and isinstance(names_data[0], str):
        # Legacy format - convert strings to NameEntry objects
        names = [
            NameEntry(name=name, translation=data.get("translation", ""), is_weak=False)
            for name in names_data
        ]
    else:
        names = []

    return Entity(
        names=names,
        entity_type=entity_type,
        description=data.get("description", ""),
        chapter_idx=data.get("chapter_idx", []),
        properties=data.get("properties", {}),
    )


def create_triplet_from_dict(data: Dict[str, Any]) -> InputTriplet:
    """
    Create a Triplet object from a dictionary

    Args:
        data: Dictionary containing triplet data

    Returns:
        Triplet object
    """
    metadata_dict = data.get("relationship_props", {})

    metadata = TripletMetadata(
        chapter_idx=metadata_dict.get("chapter_idx", 0),
        temporal_type=metadata_dict.get("temporal_type"),
        statement_type=metadata_dict.get("statement_type"),
        importance=metadata_dict.get("confidence"),
        tense_type=metadata_dict.get("tense_type"),
        source_text=metadata_dict.get("source_text"),
        additional_props=metadata_dict.get("additional_props", {}),
    )
    if data["direction"] == "outgoing":
        direction = Direction.OUTGOING
    elif data["direction"] == "incoming":
        direction = Direction.INCOMING
    else:
        raise ValueError(f"value {data["direction"]} not an option for triplet direction")

    return InputTriplet(
        subject_name=data["entity"],
        predicate=data["relationship_type"],
        object_name=data["related_entity"],
        metadata=metadata,
        direction=direction,
    )


def merge_entity_names(
    existing_names: List[NameEntry], new_names: List[NameEntry]
) -> List[NameEntry]:
    """
    Merge entity names, avoiding duplicates

    Args:
        existing_names: Current entity NameEntry objects
        new_names: New NameEntry objects to add

    Returns:
        Merged list of unique NameEntry objects
    """
    # Convert to sets for efficient operations based on name
    existing_set = set(entry.name.lower() for entry in existing_names)
    merged_names = existing_names.copy()

    for new_entry in new_names:
        if new_entry.name.lower() not in existing_set:
            merged_names.append(new_entry)
            existing_set.add(new_entry.name.lower())

    return merged_names


def find_entity_name_match(
    target_name: str, entity_names: List[NameEntry]
) -> Optional[NameEntry]:
    """
    Find if a target name matches any entity names (case-insensitive)

    Args:
        target_name: Name to search for
        entity_names: List of NameEntry objects to search in

    Returns:
        Matching NameEntry if found, None otherwise
    """
    target_lower = target_name.lower()
    for name_entry in entity_names:
        if name_entry.name.lower() == target_lower:
            return name_entry
    return None


def validate_triplet(
    triplet: InputTriplet, available_entities: List[Entity]
) -> Tuple[bool, str]:
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
        entity_names.update(name_entry.name.lower() for name_entry in entity.names)

    subject_found = triplet.subject_name.lower() in entity_names
    object_found = triplet.object_name.lower() in entity_names

    if not subject_found and not object_found:
        return (
            False,
            f"Neither subject '{triplet.subject_name}' nor object '{triplet.object_name}' found",
        )
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


def group_triplets_by_chapter(triplets: List[InputTriplet]) -> Dict[int, List[InputTriplet]]:
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


def filter_triplets_by_confidence(
    triplets: List[InputTriplet], min_confidence: float
) -> List[InputTriplet]:
    """
    Filter triplets by minimum confidence threshold

    Args:
        triplets: List of triplets to filter
        min_confidence: Minimum confidence score (0-1)

    Returns:
        Filtered list of triplets
    """
    return [
        triplet
        for triplet in triplets
        if triplet.metadata.confidence is not None
        and triplet.metadata.confidence >= min_confidence
    ]


def get_entity_summary(entity: Entity) -> str:
    """
    Generate a human-readable summary of an entity

    Args:
        entity: Entity to summarize

    Returns:
        Summary string
    """
    names_str = ", ".join(name_entry.name for name_entry in entity.names)
    summary = f"{entity.entity_type.value}: {names_str}"

    if entity.description:
        summary += f" - {entity.description}"

    if entity.chapter_idx:
        chapters_str = ", ".join(map(str, entity.chapter_idx))
        summary += f" (Chapters {chapters_str})"

    return summary

    if entity.chapter_idx is not None:
        summary += f" (Chapter {entity.chapter_idx})"

    return summary


def get_triplet_summary(triplet: InputTriplet) -> str:
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


def detect_potential_duplicates(
    entities: List[Entity], similarity_threshold: float = 0.8
) -> List[Tuple[Entity, Entity, float]]:
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
        for j, entity2 in enumerate(entities[i + 1 :], i + 1):
            max_similarity = 0.0

            # Check similarity between all name combinations
            for name_entry1 in entity1.names:
                for name_entry2 in entity2.names:
                    # Simple Jaccard similarity based on character n-grams
                    similarity = _calculate_simple_similarity(
                        name_entry1.name.lower(), name_entry2.name.lower()
                    )
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
    bigrams1 = set(str1[i : i + 2] for i in range(len(str1) - 1))
    bigrams2 = set(str2[i : i + 2] for i in range(len(str2) - 1))

    if not bigrams1 and not bigrams2:
        return 1.0
    if not bigrams1 or not bigrams2:
        return 0.0

    # Jaccard similarity
    intersection = len(bigrams1.intersection(bigrams2))
    union = len(bigrams1.union(bigrams2))

    return intersection / union if union > 0 else 0.0


def reconstruct_entities(unstructured_entities: List[Dict]) -> List[Entity]:
    """
    Reconstruct Entity objects from Neo4j dictionary data

    Args:
        unstructured_entities: List of dictionaries containing Neo4j node properties

    Returns:
        List of Entity objects
    """
    entity_list = []
    for unstructured_entity in unstructured_entities:
        name_entry_list = []
        for i in range(len(unstructured_entity["names_list"])):
            try:
                name_entry_list.append(
                    NameEntry(
                        name=unstructured_entity["names_list"][i],
                        translation=unstructured_entity["translations_list"][i],
                        is_weak=unstructured_entity["is_weak_list"][i],
                    )
                )
            except:
                raise ValueError(
                    "Fatal error with data entry, name list not correlated to values"
                )

        entity_list.append(
            Entity(
                names=name_entry_list,
                entity_type=EntityType(unstructured_entity["entity_type"]),
                description=unstructured_entity.get("description", ""),
                chapter_idx=unstructured_entity.get("chapter_idx", []),
                properties=unstructured_entity.get("properties", {}),
            )
        )
    return entity_list
