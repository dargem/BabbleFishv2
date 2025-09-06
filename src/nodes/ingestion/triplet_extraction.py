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

from ...models import TranslationState
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from ...config import config
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any


class TripletMetadata(BaseModel):
    temporal_type: str = Field(..., description="")
    statement_type: str = Field(..., description="")
    confidence: float = Field(
        ...,
        description="A number between 0 and 1 indicating the confidence of this triplet",
    )  # change to strength?
    additional_props: Optional[Dict[str, Any]] = Field(
        default=None,
        description="An optional field, add if you want to contextualise the triplet",
    )


class TripletSchema(BaseModel):
    subject: str = (Field(..., description="the subject of the triplet"),)
    predicate: str = Field(..., description="the action of the subject on the object")
    object: str = Field(..., description="the object receiving the subject's action")
    metadata: TripletMetadata = Field(
        ..., description="The metadata related to this triplet"
    )


def triplet_extractor_node(state: TranslationState):
    llm = config.get_llm()

    prompt = PromptTemplate(
        input_variables=["text", "language"],
        template="""
        {% macro tidy(name) -%}
        {{ name.replace('_', ' ')}}
        {%- endmacro %}

        You are an expert finance professional and information-extraction assistant.

        ===Inputs===
        {% if inputs %}
        {% for key, val in inputs.items() %}
        - {{ key }}: {{val}}
        {% endfor %}
        {% endif %}

        ===Tasks===
        1. Identify and extract atomic declarative statements from the chunk given the extraction guidelines
        2. Label these (1) as Fact, Opinion, or Prediction and (2) temporally as Static or Dynamic

        ===Extraction Guidelines===
        - Structure statements to clearly show subject-predicate-object relationships
        - Each statement should express a single, complete relationship (it is better to have multiple smaller statements to achieve this)
        - Avoid complex or compound predicates that combine multiple relationships
        - Must be understandable without requiring context of the entire document
        - Should be minimally modified from the original text
        - Must be understandable without requiring context of the entire document,
            - resolve co-references and pronouns to extract complete statements, if in doubt use main_entity for example:
            "your nearest competitor" -> "main_entity's nearest competitor"
            - There should be no reference to abstract entities such as 'the company', resolve to the actual entity name.
            - expand abbreviations and acronyms to their full form

        - Statements are associated with a single temporal event or relationship
        - Include any explicit dates, times, or quantitative qualifiers that make the fact precise
        - If a statement refers to more than 1 temporal event, it should be broken into multiple statements describing the different temporalities of the event.
        - If there is a static and dynamic version of a relationship described, both versions should be extracted

        {%- if definitions %}
        {%- for section_key, section_dict in definitions.items() %}
        ==== {{ tidy(section_key) | upper }} DEFINITIONS & GUIDANCE ====
            {%- for category, details in section_dict.items() %}
        {{ loop.index }}. {{ category }}
        - Definition: {{ details.get("definition", "") }}
            {% endfor -%}
        {% endfor -%}
        {% endif -%}

        ===Examples===
        Example Chunk: '''
        TechNova Q1 Transcript (Edited Version)
        Attendees:
        * Matt Taylor
            ABC Ltd - Analyst
        * Taylor Morgan
            BigBank Senior - Coordinator
        ----
        On April 1st, 2024, John Smith was appointed CFO of TechNova Inc. He works alongside the current Senior VP Olivia Doe. He is currently overseeing the company’s global restructuring initiative, which began in May 2024 and is expected to continue into 2025.
        Analysts believe this strategy may boost profitability, though others argue it risks employee morale. One investor stated, “I think Jane has the right vision.”
        According to TechNova’s Q1 report, the company achieved a 10% increase in revenue compared to Q1 2023. It is expected that TechNova will launch its AI-driven product line in Q3 2025.
        Since June 2024, TechNova Inc has been negotiating strategic partnerships in Asia. Meanwhile, it has also been expanding its presence in Europe, starting July 2024. As of September 2025, the company is piloting a remote-first work policy across all departments.
        Competitor SkyTech announced last month they have developed a new AI chip and launched their cloud-based learning platform.
        '''

        Example Output: {
        "statements": [
            {
            "statement": "Matt Taylor works at ABC Ltd.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "Matt Taylor is an Analyst.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "Taylor Morgan works at BigBank.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "Taylor Morgan is a Senior Coordinator.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "John Smith was appointed CFO of TechNova Inc on April 1st, 2024.",
            "statement_type": "FACT",
            "temporal_type": "STATIC"
            },
            {
            "statement": "John Smith has held position CFO of TechNova Inc from April 1st, 2024.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "Olivia Doe is the Senior VP of TechNova Inc.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "John Smith works with Olivia Doe.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "John Smith is overseeing TechNova Inc's global restructuring initiative starting May 2024.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "Analysts believe TechNova Inc's strategy may boost profitability.",
            "statement_type": "OPINION",
            "temporal_type": "STATIC"
            },
            {
            "statement": "Some argue that TechNova Inc's strategy risks employee morale.",
            "statement_type": "OPINION",
            "temporal_type": "STATIC"
            },
            {
            "statement": "An investor stated 'I think John has the right vision' on an unspecified date.",
            "statement_type": "OPINION",
            "temporal_type": "STATIC"
            },
            {
            "statement": "TechNova Inc achieved a 10% increase in revenue in Q1 2024 compared to Q1 2023.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "It is expected that TechNova Inc will launch its AI-driven product line in Q3 2025.",
            "statement_type": "PREDICTION",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "TechNova Inc started negotiating strategic partnerships in Asia in June 2024.",
            "statement_type": "FACT",
            "temporal_type": "STATIC"
            },
            {
            "statement": "TechNova Inc has been negotiating strategic partnerships in Asia since June 2024.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "TechNova Inc has been expanding its presence in Europe since July 2024.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "TechNova Inc started expanding its presence in Europe in July 2024.",
            "statement_type": "FACT",
            "temporal_type": "STATIC"
            },
            {
            "statement": "TechNova Inc is going to pilot a remote-first work policy across all departments as of September 2025.",
            "statement_type": "FACT",
            "temporal_type": "STATIC"
            },
            {
            "statement": "SkyTech is a competitor of TechNova.",
            "statement_type": "FACT",
            "temporal_type": "DYNAMIC"
            },
            {
            "statement": "SkyTech developed new AI chip.",
            "statement_type": "FACT",
            "temporal_type": "STATIC"
            },
            {
            "statement": "SkyTech launched cloud-based learning platform.",
            "statement_type": "FACT",
            "temporal_type": "STATIC"
            }
        ]
        }
        ===End of Examples===

        **Output format**
        Return only a list of extracted labelled statements in the JSON ARRAY of objects that match the schema below:
        {{ json_schema }}
        """,
    )

    pass
