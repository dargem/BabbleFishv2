"""Core domain models for the knowledge graph"""

from .entities import (
    Entity,
    EntityType,
    NameEntry,
)

from .relationships import (
    InputTriplet,
    OutputTriplet,
    TripletMetadata,
    TemporalType,
    StatementType,
    TenseType,
    PredicateType,
    Direction,
)

from .novels import (
    Novel,
    Chapter,
    Genre,
    Requirement,
    LanguageType,
)

__all__ = [
    "Entity",
    "EntityType",
    "InputTriplet",
    "OutputTriplet",
    "TripletMetadata",
    "NameEntry",
    "TemporalType",
    "StatementType",
    "TenseType",
    "PredicateType",
    "Direction",
    "Novel",
    "Chapter",
    "Genre",
    "Requirement",
    "LanguageType",
]
