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

# type hints
from __future__ import annotations
from src.providers import LLMProvider
from src.knowledge_graph import KnowledgeGraphManager

# imports
from ..states import IngestionState
from src.core import (
    TemporalType,
    StatementType,
    TenseType,
    PredicateType,
    Triplet,
    TripletMetadata,
)
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from pydantic import BaseModel, Field
from typing import Optional, List
import textwrap


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


# experiment with enum vs str, need to find a good prompt first
class TripletSchema(BaseModel):
    subject: str = Field(
        ..., description="The subject of the triplet, must be a singular Named Entity"
    )
    predicate: str = Field(
        ..., description="The relationship the subject has with the object"
    )
    object: str = Field(
        ...,
        description="The object receiving the subject's action, must be a singular Named Entity",
    )
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


class TripletCreator:
    """Generates triplets"""

    def __init__(self, llm_provider: LLMProvider, kg_manager: KnowledgeGraphManager):
        self.llm_provider = llm_provider
        self.kg_manager = kg_manager

    async def create_triplets(self, state: IngestionState) -> dict[str, List[Triplet]]:
        print("Finding triplets...")

        prompt = PromptTemplate(
            input_variables=["text"],
            template=textwrap.dedent("""
            You are a meticulous Knowledge Graph Architect. Your sole purpose is to extract enduring, high-value facts to build an encyclopedia-like knowledge base. You are not a story summarizer.

            Your task is to analyze the provided text and extract factual triplets. A triplet is an atomic piece of knowledge represented as **Subject (Named Entity) — Predicate — Object (Named Entity or Value)**.

            Think of it this way: you are building a character sheet or a Wikipedia entry, not writing a scene summary. A character sheet says "Character: Klein Moretti, Occupation: Detective", it does not say "Character: Klein Moretti, Action: Cleaned a wound".

            ---
            ### CRITICAL RULE: State vs. Event

            This is the most important rule. You must distinguish between a **State** (a durable fact) and an **Event** (a temporary action or occurrence).

            -   **STATE (Extract These):** Facts about identity, roles, capabilities, ownership, or fundamental relationships. These are things that are true for a sustained period.
                -   *Example:* `(Maria Gonzalez, member of, World Health Organization)`, `(Mount Everest, height, 8848 meters)`, `(Klein Moretti, possesses, a revolver)`

            -   **EVENT (IGNORE THESE):** Actions, temporary conditions, dialogue, thoughts, feelings, or scenes. These are things that happen at a specific moment in the narrative.
                -   *Example to IGNORE:* "Maria walked to the store", "The mountain was covered in snow", "Klein was suffering from a wound".

            ---
            ### Step-by-Step Extraction Process

            Follow this process precisely:

            1.  **Identify Entities:** First, identify all the key named entities (people, places, organizations, concepts) in the text.
            2.  **Analyze Relationships:** For each entity, scan the text for statements that describe its nature, role, capabilities, or relationship to other entities.
            3.  **Apply the State vs. Event Filter:** For each potential fact, ask yourself: "Is this a durable, encyclopedia-worthy fact (a State), or is this just something happening in the moment (an Event)?"
                -   If it's an **Event**, **discard it immediately**. Do not create a triplet for it.
                -   If it's a **State**, proceed to the next step.
            4.  **Coreference Resolution:** Ensure all subjects and objects are specific named entities. Replace pronouns like "he," "she," "it," or vague terms like "the man" with the actual entity's name (e.g., "Klein Moretti").
            5.  **Construct the Triplet:** Formulate the final triplet with a clear, concise predicate.
            6.  **Add Metadata:** Assign the required labels to the final, filtered triplet.

            ---
            ### Examples of What to AVOID

            Based on the text "Suffering from a grievous wound, Klein Moretti, the detective, quickly cleaned his revolver before Benson installed the new gas lamp."

            | Source Text Fragment                           |  BAD Triplet (This is an Event/Temporary State)                  | Why it's BAD                                                                |
            | ---------------------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------  |
            | "Suffering from a grievous wound"              | `(Klein Moretti, has attribute, suffering from grievous wound)`  | This is a temporary medical condition, not a permanent attribute. IGNORE.   |
            | "Klein Moretti... cleaned his revolver"        | `(Klein Moretti, participated in, cleaning his revolver)`        | This is a mundane, one-time action. IGNORE.                                 |
            | "Benson installed the new gas lamp"            | `(Benson, participated in, installing gas lamp)`                 | This is a narrative action, not a core fact about Benson's identity. IGNORE.|

            ### Examples of What to EXTRACT

            | Source Text Fragment                           | GOOD Triplet (This is a State/Durable Fact)                 | Why it's GOOD                                                        |
            | ---------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------- |
            | "Klein Moretti, the detective..."              | `(Klein Moretti, works as, Detective)`                      | This describes his profession, a durable role.                       |
            | "...cleaned his revolver..."                   | `(Klein Moretti, possesses, revolver)`                      | The ownership of the revolver is a durable fact about him.           |
            | "The currency of the Loen Kingdom is the soli" | `(Loen Kingdom, has currency, Soli)`                        | This is a fundamental, static fact about the kingdom.                |
            | "The ritual requires three sacred leaves"      | `(Luck Enhancement Ritual, requires, three sacred leaves)`  | This is a rule or requirement, a piece of knowledge about a system.  |

            ---
            ### Output Metadata Schema

            For each valid triplet you extract, provide these labels:

            -   **Temporal Type:** `Static` (unlikely to change), `Dynamic` (can change, e.g., a job title), or `Atemporal` (a rule or definition).
            -   **Statement Type:** `Fact`, `Opinion`, or `Prediction`.
            -   **Tense Type:** `Past` or `Present`.
            -   **Importance:** A score from `0` to `100` indicating how crucial this fact is to understanding the entity.

            ---
            ### TASK

            Now, analyze the following text. Following the step-by-step process and all rules, extract high-value, encyclopedia-worthy triplets.

            {text}
            """),
        )

        message = HumanMessage(content=prompt.format(text=state["text"]))
        unparsed_triplets = await self.llm_provider.schema_invoke(
            messages=[message], schema=TripletSchemaList
        )
        parsed_triplets = triplet_schema_decomposer(unparsed_triplets)
        self.kg_manager.add_triplets(parsed_triplets)
        return {"triplets": parsed_triplets}
