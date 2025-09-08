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
        description="An optional field, add if you want to place more entries to contextualise the triplet",
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
                metadata=triplet_metadata_decomposer(triplet)
            )
        )
    return triplet_list


def triplet_extractor_node(state: IngestionState):
    print("Finding triplets...")
    llm = config.get_llm(schema=TripletSchemaList)

    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        You are an expert information-extraction assistant.

        ===Tasks===
        1. Identify and extract as many triplets as possible from the chunk given according to the extraction guidelines
        2. Label triplets as temporally Static, Dynamic, or Atemporal
            - Static facts often describe a singular point in time
                - They are always valid at the point they occurred
                - For example the following are static:
                    - The company was founded in 1998
                    - X resulted in Y
            - Dynamic facts describe a period in time
                - They are valid at the point they occurred, but also into the future or past
                - For example the following are dynamically:
                    - John is the mayor
                    - The economy is shrinking
            - Atemporal facts describe absolute truths
                - They are always valid, both in present past and future
                - For example the following are atemporal:
                    - The speed of light in a vacuum is ≈3x10⁸ ms⁻¹
                    - The moon orbits the earth
                    - Water boils at 100 degrees celsius
        3. Classify as a Fact, Opinion, or Prediction
            - Facts are verifiably true at the time of the claim
            - Opinions are subjectively true considering the speakers judgement
            - Predictions are hypotheticals
        4. Classify the tense of the triplet as present or past
            - Past is applicable if its part of a flashback sequence or the triplet refers to a past event
                - e.g. Bob used to like Nike would be resolved into the triplet of Bob liking Nike resolved as past.
            - Present is the present part of the story which is currently happening, doesn't include flashbacks.
        4. Judge the importance of the triplet from a scale of 0 to 100
            - 100 is for highly important triplets containing essential information
            - 20 would connote low importance
        5. Optionally add additional propositions to the triplet if contextualisation required

        ===Extraction Guidelines===
        - Follow the json output structure to clearly show subject-predicate-object relationships
            - Subject is the action maker
            - Predicate is the action
            - Object is the receiver of the action
        - Each triplet should express a single, complete relationship (it is a good idea to split a statement into multiple triplets to achieve this)
        - Avoid complex or compound predicates that combine multiple relationships
        - Must be understandable without requiring context of the entire document
        - Should be minimally modified from the original text
        - Must be understandable without requiring context of the entire document,
            - resolve co-references and pronouns to extract complete statements, if in doubt use main_entity for example:
            "your nearest competitor" -> "main_entity's nearest competitor"
            - There should be no reference to abstract entities such as 'the company', resolve to the actual entity name.
            - expand abbreviations and acronyms to their full form

        - Include any explicit dates, times, or quantitative qualifiers that make the fact precise in the metadata
        - If a triplet refers to more than 1 temporal event, it should be broken into multiple statements describing the different temporalities of the event.

        ===Text for Triplet Extraction===
        {text}
        """,
    )

    message = HumanMessage(content=prompt.format(text=state["text"]))
    # parser needed!
    unparsed_triplets=llm.invoke([message])
    parsed_triplets = triplet_schema_decomposer(unparsed_triplets)
    for triplet in parsed_triplets:
        print(triplet.subject_name, triplet.predicate, triplet.object_name)
        print(triplet.metadata.__dict__)

