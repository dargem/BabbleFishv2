"""
triplet extraction
    - subject predicate object
    with metadata
    temporal validation labels it as one of the following:
        - Atemporal (never changing, Jill is the sister of Bob)
        - Static (Valid from a point, not changing afterwards, Bob was alive on the 23rd of January, could change later)
        - Dynamic (Changing statements which are evolving, Bob is in Hillsbury. This should "expire")
    statement types:
        - Fact (verifiably true at the time of claim)
        - Opinion (subjectively true considering the speakers judgement)
        - Prediction (Forward looking hypothetical about a potential future event) *prediction probably not needed
    temporal extraction
        - Log by chapter
        - Possible error with a flashback, etc or referring to past events
        - May have difficulties as can't resolve to a date
        - Probably filter to exclude by llm?
"""

from ...models import (
    IngestionState,
    TemporalType,
    StatementType,
    TenseType,
    Triplet,
    TripletMetadata,
)
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from ...config import config
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List


class TripletMetadataSchema(BaseModel):
    temporal_type: TemporalType = Field(
        ..., description="The temporal category of the triplet"
    )
    statement_type: StatementType = Field(
        ..., description="The statement type of the triplet"
    )
    tense_type: TenseType = Field(..., description="The relative tense of the triplet")
    importance: float = Field(
        ...,
        description="A number between 0 and 100 indicating the importance of this triplet",
    )
    additional_props: Optional[str] = Field(
        default=None,
        description="An optional field, add if you want to add more information, triplets won't have the original text for context",
    )


class TripletSchema(BaseModel):
    subject: str = Field(..., description="The subject of the triplet")
    predicate: str = Field(..., description="The action of the subject on the object")
    object: str = Field(..., description="The object receiving the subject's action")
    metadata: TripletMetadataSchema = Field(
        ..., description="The metadata related to this triplet"
    )


class TripletSchemaList(BaseModel):
    triplet_list: List[TripletSchema] = Field(
        ..., description="A list of triplets made from the text"
    )


def triplet_metadata_decomposer(triplet: TripletSchema) -> TripletMetadata:
    metadata = triplet.metadata
    return TripletMetadata(
        chapter_idx=0,
        temporal_type=metadata.temporal_type,
        statement_type=metadata.statement_type,
        tense_type=metadata.tense_type,
        importance=metadata.importance,
        source_text="LOTM",
        additional_props=metadata.additional_props,
    )


def triplet_schema_decomposer(triplets: TripletSchemaList) -> List[Triplet]:
    triplet_list = []
    triplet_schema_list = triplets.triplet_list
    for triplet in triplet_schema_list:
        triplet_list.append(
            Triplet(
                subject_name=triplet.subject,
                predicate=triplet.predicate,
                object_name=triplet.object,
                metadata=triplet_metadata_decomposer(triplet),
            )
        )
    return triplet_list


def triplet_extractor_node(state: IngestionState):
    print("Finding triplets...")
    llm = config.get_llm(schema=TripletSchemaList)

    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        You are an expert information-extraction assistant. Your task is to extract **high-importance, context-independent triplets** suitable for a knowledge base or knowledge graph.

        === Triplet Definition ===

        A triplet is a single, abstracted fact expressed as:  
        **Subject (Named Entity) — Predicate — Object (Named Entity, Attribute, Possession, Location, Ability, Role, or Quantifiable Fact)**  
        A triplet is *NOT THE ORIGINAL TEXT*, it is a modi
        
        Rules for triplets:

        1. **Do not include narrative actions, thoughts, or mundane events.**  
        - Example to exclude: "Alice picked up a pen", "John walked to the store".  
        2. **At all costs never include vague pronouns, articles, or undefined entities.**  
        - Example to exclude: "it", "himself", "this", "the object", "his".
        - Grammatical clarity does not matter, ensure all entities are resolved at all costs
        3. **Always perform coreference resolution.**  
        - Replace pronouns or vague references with the correct named entity.  
        4. **Only extract triplets with meaningful, knowledge-worthy information.**  

        Acceptable triplets include:  
        - Relationships between named entities (people, organizations, institutions).  
        - Example: "Maria Gonzalez — member of — World Health Organization"  
        - Roles, titles, occupations, or official positions.  
        - Example: "Thomas Clarke — works as — Biochemist"  
        - Abilities, powers, rituals, supernatural rules, or procedural requirements.  
        - Example: "Fire Ritual — requires — three sacred leaves from Grynn"  
        - Important locations, historical facts, or possessions of entities.  
        - Example: "Alexander Hamilton — founded — Bank of New York"  
        - Quantifiable or verifiable facts about named entities.  
        - Example: "Mount Everest — height — 8848 meters"  

        === Temporal and Context Labels ===  

        Each triplet must be labeled as:  
        - **Temporal Type:** Static, Dynamic, or Atemporal  
        - **Statement Type:** Fact, Opinion, Prediction  
        - **Tense Type:** Past, Present  
        - **Importance:** 0-100  

        Optional: Add additional propositions for clarity if needed.

        === Key Filters ===  

        - Never output generic events or trivial narrative actions, even if they involve named entities.  
        - Never include abstract, speculative, or rhetorical statements.  
        - Triplets must be fully understandable **without reading the source text**.  
        - Only include **knowledge-worthy relationships or attributes**.  

        === Extraction Guidelines ===

        1. Resolve all pronouns to named entities.  
        2. Extract only **high-value, concrete facts**.  
        3. Avoid compound predicates; break multi-fact statements into separate triplets.  
        4. Include explicit dates, numbers, or qualifiers if available.  
        5. If a fact is temporary or procedural, label appropriately (Dynamic).  
        6. Abstract narrative actions into knowledge-worthy facts only if they convey abilities, powers, or roles.

        === Task ===

        Extract **only triplets that meet these criteria**. Ignore everything else.

        {text}
        """,
    )

    message = HumanMessage(content=prompt.format(text=state["text"]))
    # parser needed!
    unparsed_triplets = llm.invoke([message])
    parsed_triplets = triplet_schema_decomposer(unparsed_triplets)
    for triplet in parsed_triplets:
        if triplet.metadata.importance >= 0:
            print(
                f"Name: {triplet.subject_name}, Predicate: {triplet.predicate}, Object: {triplet.object_name}"
            )
            print(triplet.metadata.__dict__)
