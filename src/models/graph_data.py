"""Data models for the knowledge graph"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class EntityType(Enum):
    """The type an named entity can be"""

    CHARACTER = "Character"  # Characters like people
    PLACE = "Place"  # Cities, planets, realms, buildings
    ORGANIZATION = "Organization"  # governments, groups, societies
    EVENT = "Event"  # Wars, festivals, battles, key story events, timeperiods
    ITEM = "Item"  # Objects, weapons, artifacts, technology
    CONCEPT = "Concept"  # Abstract ideas, cultural notions, spells, powers
    TITLE = "Title"  # Named roles (King, Lord, Prophet etc.)
    WORK = "Work"  # Books, songs, prophecies, artworks within the fiction
    LANGUAGE = "Language"  # Fictional tongues, scripts, dialects
    SPECIES = "Species"  # Distinct races/lineages in the setting
    MYTH = "Myth"  # Legends, prophecies, religious/magic lore

@dataclass
class NameEntry:
    """Type of a name entry, strong name entries are grouped, weak aren't"""
    name: str
    translation: str
    is_weak: bool


@dataclass
class Entity:
    """Entity in the knowledge graph"""

    names: List[NameEntry]
    entity_type: EntityType
    description: str
    chapter_idx: List[int] # list of chapter_idx appearances
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

    def to_neo4j_props(self) -> Dict[str, Any]:
        """Convert entity to Neo4j node properties"""
        props = {
            "names": self.names,
            "weak_names": self.weak_names,
            "entity_type": self.entity_type.value,
            "chapter_idx": self.chapter_idx,
            "translation": self.translation,
            "description": self.description
        }

        if self.translation:
            props["translation"] = self.translation
        if self.description:
            props["description"] = self.description

        # Add custom properties
        props.update(self.properties)

        return props


@dataclass
class TripletMetadata:
    """Metadata for a triplet/relationship"""

    chapter_idx: int
    temporal_type: Optional[str] = None  # "static", "dynamic", "atemporal"
    statement_type: Optional[str] = None  # "fact", "opinion", "prediction"
    confidence: Optional[float] = None
    source_text: Optional[str] = None
    additional_props: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_props is None:
            self.additional_props = {}

    def to_neo4j_props(self) -> Dict[str, Any]:
        """Convert metadata to Neo4j relationship properties"""
        props = {"chapter_idx": self.chapter_idx}

        if self.temporal_type:
            props["temporal_type"] = self.temporal_type
        if self.statement_type:
            props["statement_type"] = self.statement_type
        if self.confidence is not None:
            props["confidence"] = self.confidence
        if self.source_text:
            props["source_text"] = self.source_text

        # Add additional properties
        props.update(self.additional_props)

        return props


@dataclass
class Triplet:
    """A relationship triplet between entities"""

    subject_name: str  # Name of the subject entity
    predicate: str  # The relationship type
    object_name: str  # Name of the object entity
    metadata: TripletMetadata

    def __str__(self):
        return f"({self.subject_name}) -[{self.predicate}]-> ({self.object_name})"
