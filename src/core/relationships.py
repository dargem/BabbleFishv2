"""Edge based data models for the knowledge graph"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class PredicateType(Enum):
    """Enumeration of normalized predicates for fiction and worldbuilding."""

    # Identity & Roles
    IS_A = "IS_A"  # "Gandalf IS_A Wizard"
    HOLDS_TITLE = "HOLDS_TITLE"  # "Aragorn HOLDS_TITLE King of Gondor"
    MEMBER_OF = "MEMBER_OF"  # "Harry Potter MEMBER_OF Gryffindor House"
    LEADS = "LEADS"  # "Daenerys LEADS Unsullied"
    SERVES = "SERVES"  # "Sam SERVES Frodo"
    ALIAS_OF = "ALIAS_OF"  # "Clark Kent ALIAS_OF Superman"
    SUCCESSOR_TO = "SUCCESSOR_TO"  # "Joffrey SUCCESSOR_TO Robert Baratheon"
    APPRENTICE_OF = "APPRENTICE_OF"  # "Anakin Skywalker APPRENTICE_OF Obi-Wan Kenobi"

    # Relationships
    RELATED_TO = "RELATED_TO"  # Family or kinship
    ALLIED_WITH = "ALLIED_WITH"  # Allies, friends
    ENEMY_OF = "ENEMY_OF"  # Rivals, opponents
    BETRAYED = "BETRAYED"  # Betrayal events
    MENTORS = "MENTORS"  # "Obi-Wan MENTORS Luke"
    SPOUSE_OF = "SPOUSE_OF"  # "Aragorn SPOUSE_OF Arwen"
    PARENT_OF = "PARENT_OF"  # "Darth Vader PARENT_OF Luke Skywalker"
    CHILD_OF = "CHILD_OF"  # "Luke Skywalker CHILD_OF Darth Vader"
    LOVES = "LOVES"  # "Romeo LOVES Juliet"
    FEARS = "FEARS"  # "Winston Smith FEARS Rats"
    TRUSTS = "TRUSTS"  # "Frodo TRUSTS Gandalf"
    DISTRUSTS = "DISTRUSTS"  # "Boromir DISTRUSTS Saruman"

    # Locations & Possessions
    LOCATED_IN = "LOCATED_IN"  # "The One Ring LOCATED_IN Mount Doom"
    OWNS = "OWNS"  # "Smaug OWNS Treasure Hoard"
    POSSESSES = "POSSESSES"  # "Arthur POSSESSES Excalibur"
    DESTROYS = "DESTROYS"  # "Sauron DESTROYS Númenor"
    BORN_IN = "BORN_IN"  # "Superman BORN_IN Krypton"
    RULES_OVER = "RULES_OVER"  # "Sauron RULES_OVER Mordor"
    ESCAPED_FROM = "ESCAPED_FROM"  # "Edmond Dantès ESCAPED_FROM Château d'If"

    # Abilities & Powers
    HAS_POWER = "HAS_POWER"  # "Superman HAS_POWER Flight"
    USES_POWER = "USES_POWER"  # "Doctor Strange USES_POWER Time Manipulation"
    CURSED_WITH = "CURSED_WITH"  # "Frodo CURSED_WITH Burden of the Ring"
    BLESSED_BY = "BLESSED_BY"  # "Achilles BLESSED_BY Gods"
    WEAK_TO = "WEAK_TO"  # "Superman WEAK_TO Kryptonite"
    IMMUNE_TO = "IMMUNE_TO"  # "Daenerys Targaryen IMMUNE_TO Fire"
    TRANSFORMED_INTO = "TRANSFORMED_INTO"  # "The Beast TRANSFORMED_INTO Prince Adam"

    # Rituals, Magic, Lore
    PERFORMS = "PERFORMS"  # "Cult PERFORMS Dark Ritual"
    REQUIRES = "REQUIRES"  # "Dark Ritual REQUIRES Sacrifice"
    CREATED = "CREATED"  # "Morgoth CREATED Orcs"
    DESTINED_FOR = "DESTINED_FOR"  # "Prophecy DESTINED_FOR Hero"
    SUMMONS = "SUMMONS"  # "The Sorcerer SUMMONS A Demon"
    FORETOLD_BY = (
        "FORETOLD_BY"  # "Anakin's downfall FORETOLD_BY The Prophecy of the Chosen One"
    )
    DERIVES_FROM = "DERIVES_FROM"  # "The One Power DERIVES_FROM The True Source"

    # Events & Outcomes
    FOUGHT_IN = "FOUGHT_IN"  # "Jon Snow FOUGHT_IN Battle of the Bastards"
    KILLED = "KILLED"  # "Achilles KILLED Hector"
    RESCUED = "RESCUED"  # "Mario RESCUED Princess Peach"
    DIED_IN = "DIED_IN"  # "Boromir DIED_IN Amon Hen"
    RESURRECTED = "RESURRECTED"  # "Gandalf RESURRECTED After Balrog Battle"
    CAUSED = "CAUSED"  # "Icarus's hubris CAUSED His fall"
    WITNESSED = "WITNESSED"  # "Samwise Gamgee WITNESSED Boromir's death"
    PARTICIPATED_IN = (
        "PARTICIPATED_IN"  # "Bilbo Baggins PARTICIPATED_IN The Council of Elrond"
    )

    # Organizations & Factions
    PART_OF = "PART_OF"  # "Night's Watch PART_OF The Wall"
    FOUNDED = "FOUNDED"  # "Salazar Slytherin FOUNDED Slytherin House"
    RULES = "RULES"  # "Emperor Palpatine RULES Galactic Empire"
    WORSHIPS = "WORSHIPS"  # "Cult WORSHIPS Elder God"

    # Artifacts & Items
    DISCOVERED = "DISCOVERED"  # "Indiana Jones DISCOVERED Ark of the Covenant"
    GUARDS = "GUARDS"  # "Cerberus GUARDS Underworld"
    SEEKS = "SEEKS"  # "Gollum SEEKS One Ring"
    PROTECTS = "PROTECTS"  # "Knights PROTECT Holy Grail"
    WIELDS = "WIELDS"  # "Thor WIELDS Mjölnir"
    FORGED = "FORGED"  # "Celebrimbor FORGED The Rings of Power"
    CONTAINS = "CONTAINS"  # "The Tesseract CONTAINS The Space Stone"
    COMPONENT_OF = "COMPONENT_OF"  # "The Elder Wand COMPONENT_OF The Deathly Hallows"

    # Communication & Knowledge
    KNOWS_SECRET = "KNOWS_SECRET"  # "Dumbledore KNOWS_SECRET Snape's true allegiance"
    DECEIVED = "DECEIVED"  # "Othello DECEIVED Iago"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"  # "Professor X COMMUNICATES_WITH Jean Grey"


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


@dataclass
class TripletMetadata:
    """Metadata for a triplet/relationship"""

    chapter_idx: int
    temporal_type: TemporalType  # static, dynamic, atemporal
    statement_type: StatementType  # fact, opinion, prediction
    tense_type: TenseType  # current, future, past
    importance: float
    source_text: str
    additional_props: Optional[str] = None

    def __post_init__(self):
        if self.additional_props is None:
            self.additional_props = {}

    def to_neo4j_props(self) -> Dict[str, Any]:  # TODO add metadata !
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
