"""Node based data models"""

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
    chapter_idx: List[int]  # list of chapter_idx appearances
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

    @property
    def strong_names(self) -> List[str]:
        """Get all strong (non-weak) names"""
        return [entry.name for entry in self.names if not entry.is_weak]

    @property
    def weak_names(self) -> List[str]:
        """Get all weak names"""
        return [entry.name for entry in self.names if entry.is_weak]

    @property
    def all_names(self) -> List[str]:
        """Get all names (both strong and weak)"""
        return [entry.name for entry in self.names]

    @property
    def translations(self) -> Dict[str, str]:
        """Get mapping of names to their translations"""
        return {
            entry.name: entry.translation for entry in self.names if entry.translation
        }

    def get_translation_for_name(self, name: str) -> Optional[str]:
        """Get the translation for a specific name"""
        for entry in self.names:
            if entry.name.lower() == name.lower():
                return entry.translation
        return None

    def get_name_entry(self, name: str) -> Optional[NameEntry]:
        """Get the full NameEntry for a specific name"""
        for entry in self.names:
            if entry.name.lower() == name.lower():
                return entry
        return None

    def add_name_entry(self, name_entry: NameEntry) -> None:
        """Add a new name entry if it doesn't already exist"""
        existing_names = {entry.name.lower() for entry in self.names}
        if name_entry.name.lower() not in existing_names:
            self.names.append(name_entry)

    def merge_entity(self, entity: "Entity"):
        """Combines another entity with itself"""
        print(f"merging entity {entity.names[0].name} with {self.names[0].name}")
        current_names = {name_entry.name for name_entry in self.names}
        for name_entry in entity.names:
            if name_entry.name not in current_names:
                self.add_name_entry(name_entry)

        self.chapter_idx.extend(entity.chapter_idx)

    def to_neo4j_props(self) -> Dict[str, Any]:
        """Convert entity to Neo4j node properties"""
        # Store NameEntry data as separate parallel arrays that Neo4j can handle
        names_list = [entry.name for entry in self.names]
        translations_list = [entry.translation for entry in self.names]
        is_weak_list = [entry.is_weak for entry in self.names]

        props = {
            "names_list": names_list,
            "translations_list": translations_list,
            "is_weak_list": is_weak_list,
            "strong_names": self.strong_names,
            "weak_names": self.weak_names,
            "all_names": self.all_names,
            "entity_type": self.entity_type.value,
            "chapter_idx": self.chapter_idx,
            "description": self.description,
        }

        # Add custom properties
        props.update(self.properties)

        return props
