"""Core domain models for the knowledge graph"""

from .entities import (
    Entity,
    EntityType,
    NameEntry,
)
from .relationships import (
    Triplet,
    TripletMetadata,
    TemporalType,
    StatementType,
    TenseType,
    FictionPredicate,
)

__all__ = [
    "Entity",
    "EntityType",
    "Triplet",
    "TripletMetadata",
    "NameEntry",
    "TemporalType",
    "StatementType",
    "TenseType",
    "FictionPredicate",
]
