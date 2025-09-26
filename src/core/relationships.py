"""Edge based data models for the knowledge graph"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from .entities import Entity

from enum import Enum


class PredicateType(Enum):
    """Generalized predicates for entities, relationships, and attributes."""

    # Identity & Classification
    IS_A = "IS_A"  # "A IS_A Wizard"
    HAS_ROLE = "HAS_ROLE"  # "A HAS_ROLE King"
    MEMBER_OF = "MEMBER_OF"  # "A MEMBER_OF Organization"
    PART_OF = "PART_OF"  # "A PART_OF Whole"
    SUCCESSOR_OF = "SUCCESSOR_OF"  # "A SUCCESSOR_OF B"
    PREDECESSOR_OF = "PREDECESSOR_OF"  # "A PREDECESSOR_OF B"

    # Social & Familial Relationships
    FRIEND_OF = "FRIEND_OF"  # "A FRIEND_OF B"
    ALLIED_WITH = "ALLIED_WITH"  # "A ALLIED_WITH B"
    ENEMY_OF = "ENEMY_OF"  # "A ENEMY_OF B"
    SPOUSE_OF = "SPOUSE_OF"  # "A SPOUSE_OF B"
    PARENT_OF = "PARENT_OF"  # "A PARENT_OF B"
    CHILD_OF = "CHILD_OF"  # "A CHILD_OF B"
    SIBLING_OF = "SIBLING_OF"  # "A SIBLING_OF B"
    MENTOR_OF = "MENTOR_OF"  # "A MENTOR_OF B"
    APPRENTICE_OF = "APPRENTICE_OF"  # "A APPRENTICE_OF B"

    # Trust & Emotion
    TRUSTS = "TRUSTS"  # "A TRUSTS B"
    DISTRUSTS = "DISTRUSTS"  # "A DISTRUSTS B"
    LOVES = "LOVES"  # "A LOVES B"
    HATES = "HATES"  # "A HATES B"
    FEARS = "FEARS"  # "A FEARS B"
    RESPECTS = "RESPECTS"  # "A RESPECTS B"
    DISRESPECTS = "DISRESPECTS"  # "A DISRESPECTS B"
    ENVIES = "ENVIES"  # "A ENVIES B"
    ADMIRE = "ADMIRE"  # "A ADMIRE B"
    PITIES = "PITIES"  # "A PITIES B"
    BETRAYS = "BETRAYS"  # "A BETRAYS B"
    FORGIVES = "FORGIVES"  # "A FORGIVES B"
    PROTECTS = "PROTECTS"  # "A PROTECTS B"
    DEFENDS = "DEFENDS"  # "A DEFENDS B"

    # Possession & Control
    OWNS = "OWNS"  # "A OWNS B"
    GUARDS = "GUARDS"  # "A GUARDS B"
    SEEKS = "SEEKS"  # "A SEEKS B"
    CREATES = "CREATES"  # "A CREATES B"
    DESTROYS = "DESTROYS"  # "A DESTROYS B"
    LOSES = "LOSES"  # A LOSES B
    RULES_OVER = "RULES_OVER"  # "A RULES_OVER B"

    # Location & Origin
    LOCATED_IN = "LOCATED_IN"  # "A LOCATED_IN B"
    BORN_IN = "BORN_IN"  # "A BORN_IN B"
    ORIGINATES_FROM = "ORIGINATES_FROM"  # "A ORIGINATES_FROM B"
    ESCAPED_FROM = "ESCAPED_FROM"  # "A ESCAPED_FROM B"

    # Abilities & Attributes
    HAS_ATTRIBUTE = "HAS_ATTRIBUTE"  # "A HAS_ATTRIBUTE Strong"
    HAS_POWER = "HAS_POWER"  # "A HAS_POWER Flight"
    WEAK_TO = "WEAK_TO"  # "A WEAK_TO B"
    IMMUNE_TO = "IMMUNE_TO"  # "A IMMUNE_TO B"
    TRANSFORMED_INTO = "TRANSFORMED_INTO"  # "A TRANSFORMED_INTO B"

    # Knowledge & Communication
    MISUNDERSTANDS = "MISUNDERSTANDS"
    KNOWS_SECRET = "KNOWS_SECRET"  # "A KNOWS_SECRET B"
    DECEIVES = "DECEIVES"  # "A DECEIVES B"

    # Events
    PARTICIPATED_IN = "PARTICIPATED_IN"  # "A PARTICIPATED_IN Event"
    WITNESSED = "WITNESSED"  # "A WITNESSED B"
    CAUSED = "CAUSED"  # "A CAUSED B"
    AFFECTED_BY = "AFFECTED_BY"  # "A AFFECTED_BY B"
    DIED_IN = "DIED_IN"  # "A DIED_IN B"
    RESURRECTED_IN = "RESURRECTED_IN"  # "A RESURRECTED_IN B"


class TemporalType(Enum):
    static = "static"
    dynamic = "dynamic"
    atemporal = "atemporal"


class StatementType(Enum):
    fact = "fact"
    opinion = "opinion"
    prediction = "prediction"


class TenseType(Enum):
    current = "current"
    past = "past"


class Direction(Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"


@dataclass
class TripletMetadata:
    """Metadata for a triplet/relationship"""

    chapter_idx: int
    temporal_type: TemporalType  # static, dynamic, atemporal
    statement_type: StatementType  # fact, opinion, prediction
    tense_type: TenseType  # current, future, past
    importance: float
    source_text: Optional[str] = None
    additional_props: Optional[str] = None

    def __post_init__(self):
        if self.additional_props is None:
            self.additional_props = {}

    def to_neo4j_props(self) -> Dict[str, Any]:  # TODO add metadata !
        """Convert metadata to Neo4j relationship properties"""
        props = {"chapter_idx": self.chapter_idx}

        props["temporal_type"] = self.temporal_type.value
        props["statement_type"] = self.statement_type.value
        props["confidence"] = self.importance  # fix this mismatch later
        props["tense_type"] = self.tense_type.value
        if self.source_text:
            props["source_text"] = self.source_text

        # Add additional properties
        props.update(self.additional_props)

        return props


@dataclass
class InputTriplet:
    """
    A relationship triplet between entities used for input into DB
    One directional, links through strong names
    """

    subject_name: str  # Name of the subject entity
    predicate: str  # The relationship type
    object_name: str  # Name of the object entity
    metadata: TripletMetadata

    def __str__(self):
        return f"({self.subject_name}) -[{self.predicate}]-> ({self.object_name})"


@dataclass
class OutputTriplet:
    """
    A relationship triplet between entities used for output
    Compared to an input it has both direction and links entities rather than strong names
    """

    subject_name: Entity  # Name of the subject entity
    predicate: str  # The relationship type
    object_name: Entity  # Name of the object entity
    metadata: TripletMetadata

    def __str__(self):
        return f"({self.subject_name}) -[{self.predicate}]-> ({self.object_name})"
