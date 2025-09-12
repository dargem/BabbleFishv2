"""entity addition node for the translation workflow"""

# type hints
from __future__ import annotations
from src.providers import LLMProvider
from src.knowledge_graph import KnowledgeGraphManager

# imports
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from pydantic import BaseModel, Field
from typing import List
from ..states import IngestionState
from src.core import Entity, NameEntry


class TermTranslation(BaseModel):
    """Sub schema for a terms translation"""

    original_term: str = Field(
        ..., description="The original entity term from the source text."
    )
    translated_term: str = Field(
        ..., description="The translated term for the original entity."
    )


class EntitySchema(BaseModel):
    """Schema for a single named entity and its translation information."""

    name: TermTranslation = Field(
        ..., description="The core name of the entity and its translation."
    )
    entity_type: str = Field(
        ...,
        description="The category of the entity, such as Character, Place, or Organization.",
    )
    strong_matches: List[TermTranslation] = Field(
        ...,
        description="A list of terms that are strong matches for the entity, along with their translations.",
    )
    weak_matches: List[TermTranslation] = Field(
        ...,
        description="A list of terms that are weak matches for the entity, along with their translations.",
    )
    description: str = Field(
        ..., description="An in-depth description of this entity from the source text."
    )


class EntitySchemaList(BaseModel):
    entities: List[EntitySchema] = Field(..., description="A list of entity Schema")


def _name_entry_creator(
    name: TermTranslation,
    is_weak: bool,
) -> NameEntry:
    return NameEntry(
        name=name.original_term, translation=name.translated_term, is_weak=is_weak
    )


def _name_entry_list_creator(
    name_lists: List[TermTranslation], is_weak: bool
) -> List[NameEntry]:
    return [_name_entry_creator(name, is_weak) for name in name_lists]


def _entity_schema_decomposer(entity_schema_list: EntitySchemaList) -> List[Entity]:
    """Decomposes an Entity Schema List into a list of entities"""
    entity_list = []
    for entity_schema in entity_schema_list.entities:
        name_entry_list = []
        name_entry_list.append(_name_entry_creator(entity_schema.name, is_weak=False))
        name_entry_list.extend(
            _name_entry_list_creator(entity_schema.strong_matches, is_weak=False)
        )
        name_entry_list.extend(
            _name_entry_list_creator(entity_schema.weak_matches, is_weak=True)
        )
        entity_list.append(
            Entity(
                names=name_entry_list,
                entity_type=entity_schema.entity_type,  # TODO need to add stuff for enum validation still!
                description=entity_schema.description,
                chapter_idx=0,  # TODO Holder
            )
        )
    return entity_list


class EntityCreator:
    """Recognise entities from original text"""

    def __init__(self, llm_provider: LLMProvider, kg_manager: KnowledgeGraphManager):
        self.llm_provider = llm_provider
        self.kg_manager = kg_manager

    async def create_entities(self, state: IngestionState) -> dict[str,List[Entity]]:
        """
        Args:
            state: Current translation state

        Returns:
            Dictionary with nodes + reasoning
        """
        print("Finding terms...")

        template = """
        You are a translator tasked with Named Entity Reconition, identifying named terms in the following text.
        This will be later used to build a glossary so ensure unique domain specific terms are always included.
        Entities that are also likely recurring and you believe should be *consistently* translated should be added.
        
        These entities types are including but are not limited to:
            - Characters (Jim, Jack Crowley etc)
            - Places (Saint Theres Church, Hogwarts etc)
            - Items (Wand)
            - Symbols 
            - Motifs

        Avoid items that don't need consistent translation for example the date (2023, May 2021).
        A highly important domain specific date which for example might reference an event, like the 2008 for the GFC is fine.

        When multiple phrases refer to the same entity, for example with Jack and Jack Crowley to the same person perform coreference resolution.
        You can create both strong links and weak links. 
        A strong link for example would be Jack, Jack Crowley and Captain Crowley where these certainly refer to the same person.
        A weak link would be for example Captain, which could refer to Captain Crowley but also other Captains in this context.
        A weak link should be in a basic form, for example 
            - "the Captain" would be "Captain"
        
        Only create a strong link if you are absolutely certain two phrases refer to the same entity, and these are unique phrases like first/last name.
        Otherwise create weak links or no links when not necessary.

        An example translation:

        <input>
        In October 1998, Clara Mendoza moved from Seville, Spain, to Brighton, England, to begin her studies at the University of Sussex. 
        She had received a scholarship from the British Council to pursue a degree in History of Art. 
        Her first professor, Dr. Martin Holloway, introduced her to archival work at the Victoria and Albert Museum in London. 
        There, Clara uncovered letters written in 1872 by Eleanor Whitcombe, a painter who exhibited in the Royal Academy of Arts.
        </input>

        <output>
        [
            {{
                "name": {{
                "original_term": "Clara Mendoza",
                "translated_term": "Clara Mendoza"
                }},
                "entity_type": "Character",
                "strong_matches": [],
                "weak_matches": [
                {{
                    "original_term": "Clara",
                    "translated_term": "Clara"
                }}
                ],
                "description": "A student who moved from Seville, Spain to Brighton, England to study at the University of Sussex."
            }},
            {{
                "name": {{
                "original_term": "Seville",
                "translated_term": "Seville"
                }},
                "entity_type": "Place",
                "strong_matches": [],
                "weak_matches": [],
                "description": "A city in Spain where Clara Mendoza lived before moving to Brighton."
            }},
            {{
                "name": {{
                "original_term": "Spain",
                "translated_term": "Spain"
                }},
                "entity_type": "Place",
                "strong_matches": [],
                "weak_matches": [],
                "description": "The country of origin for Clara Mendoza."
            }},
            {{
                "name": {{
                "original_term": "Brighton",
                "translated_term": "Brighton"
                }},
                "entity_type": "Place",
                "strong_matches": [],
                "weak_matches": [],
                "description": "A city in England where Clara Mendoza moved to for her studies."
            }},
            {{
                "name": {{
                "original_term": "England",
                "translated_term": "England"
                }},
                "entity_type": "Place",
                "strong_matches": [],
                "weak_matches": [],
                "description": "The country where Clara Mendoza pursued her studies."
            }},
            {{
                "name": {{
                "original_term": "University of Sussex",
                "translated_term": "University of Sussex"
                }},
                "entity_type": "Organization",
                "strong_matches": [],
                "weak_matches": [],
                "description": "The university Clara Mendoza attended."
            }},
            {{
                "name": {{
                "original_term": "British Council",
                "translated_term": "British Council"
                }},
                "entity_type": "Organization",
                "strong_matches": [],
                "weak_matches": [],
                "description": "The organization that provided a scholarship to Clara Mendoza."
            }},
            {{
                "name": {{
                "original_term": "History of Art",
                "translated_term": "History of Art"
                }},
                "entity_type": "Academic Subject",
                "strong_matches": [],
                "weak_matches": [],
                "description": "The degree Clara Mendoza pursued."
            }},
            {{
                "name": {{
                "original_term": "Dr. Martin Holloway",
                "translated_term": "Dr. Martin Holloway"
                }},
                "entity_type": "Character",
                "strong_matches": [],
                "weak_matches": [
                {{
                    "original_term": "Dr. Holloway",
                    "translated_term": "Dr. Holloway"
                }},
                {{
                    "original_term": "Dr. Martin",
                    "translated_term": "Dr. Martin"
                }}
                ],
                "description": "Clara Mendoza's first professor who introduced her to archival work."
            }},
            {{
                "name": {{
                "original_term": "Victoria and Albert Museum",
                "translated_term": "Victoria and Albert Museum"
                }},
                "entity_type": "Place",
                "strong_matches": [
                {{
                    "original_term": "Victoria and Albert Museum in London",
                    "translated_term": "Victoria and Albert Museum in London"
                }}
                ],
                "weak_matches": [],
                "description": "The museum in London where Clara Mendoza performed archival work."
            }},
            {{
                "name": {{
                "original_term": "London",
                "translated_term": "London"
                }},
                "entity_type": "Place",
                "strong_matches": [],
                "weak_matches": [],
                "description": "The city where the Victoria and Albert Museum is located."
            }},
            {{
                "name": {{
                "original_term": "Eleanor Whitcombe",
                "translated_term": "Eleanor Whitcombe"
                }},
                "entity_type": "Character",
                "strong_matches": [],
                "weak_matches": [
                {{
                    "original_term": "a painter",
                    "translated_term": "a painter"
                }}
                ],
                "description": "A painter from 1872 whose letters were uncovered by Clara Mendoza."
            }},
            {{
                "name": {{
                "original_term": "Royal Academy of Arts",
                "translated_term": "Royal Academy of Arts"
                }},
                "entity_type": "Organization",
                "strong_matches": [],
                "weak_matches": [],
                "description": "The organization where Eleanor Whitcombe exhibited her paintings."
            }}
        ]
        </output>
        Prioritise finding as many entities as you can. The more entities you find the better, output one for all characters at the bare minimum. 
        Do not include anything except json form output.

        Text: {text}
        """

        prompt = PromptTemplate(input_variables=["text"], template=template)

        message = HumanMessage(content=prompt.format(text=state["text"]))

        unparsed_entities = await self.llm_provider.schema_invoke(
            messages=[message],
            schema=EntitySchemaList,
        )

        entities = _entity_schema_decomposer(unparsed_entities)

        # TODO add unification with the database and entity class later
        return {"entities": entities}
