"""entity addition node for the translation workflow, paired with the removal node"""

from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from typing import List

from ...models import TranslationState
from ...config import config

ingestion_schema = {
    "Name": str,
    "Type": str,
    "Strong Match": List[str],
    "Weak Match": List[str],
    "Description": str,
    "Summary": str,
}

def entity_addition_node(state: TranslationState) -> dict:
    """Recognise entities from original text.

    Args:
        state: Current translation state

    Returns:
        Dictionary with nodes + reasoning
    """
    print("Finding terms...")
    print(state)
    llm = config.get_llm(schema=None) # for now ingestion schema doesn't seem to be working

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
    
    This is an example json output.
    {{
        "Name": str,
        "Type": str,
        "Strong Match": List[str],
        "Weak Match": List[str],
        "Description": str,
        "Summary": str,
    }}

    <input>
    In October 1998, Clara Mendoza moved from Seville, Spain, to Brighton, England, to begin her studies at the University of Sussex. 
    She had received a scholarship from the British Council to pursue a degree in History of Art. 
    Her first professor, Dr. Martin Holloway, introduced her to archival work at the Victoria and Albert Museum in London. 
    There, Clara uncovered letters written in 1872 by Eleanor Whitcombe, a painter who exhibited in the Royal Academy of Arts.
    </input>

    <output>
    [
        {{
            "Name": "Clara Mendoza",
            "Type": "Character",
            "Strong Match": ["Clara", "Clara Mendoza"],
            "Weak Match": [],
            "Description": "A Spanish student who moved from Seville to Brighton in 1998 to study History of Art at the University of Sussex.",
            "Summary": "Main subject of the passage, likely recurring individual."
        }},
        {{
            "Name": "Seville",
            "Type": "Place",
            "Strong Match": ["Seville"],
            "Weak Match": [],
            "Description": "A city in Spain, the place where Clara Mendoza lived before moving.",
            "Summary": "Place of origin for Clara."
        }},
        {{
            "Name": "Spain",
            "Type": "Place",
            "Strong Match": ["Spain"],
            "Weak Match": [],
            "Description": "Country where Seville is located.",
            "Summary": "Clara’s country of origin."
        }},
        {{
            "Name": "Brighton",
            "Type": "Place",
            "Strong Match": ["Brighton"],
            "Weak Match": [],
            "Description": "City in England where Clara moved for her studies.",
            "Summary": "New residence for Clara."
        }},
        {{
            "Name": "England",
            "Type": "Place",
            "Strong Match": ["England"],
            "Weak Match": [],
            "Description": "Country where Brighton is located.",
            "Summary": "Destination country of Clara’s move."
        }},
        {{
            "Name": "University of Sussex",
            "Type": "Place",
            "Strong Match": ["University of Sussex"],
            "Weak Match": ["the University"],
            "Description": "The university where Clara pursued a degree in History of Art.",
            "Summary": "Institution of Clara’s studies."
        }},
        {{
            "Name": "British Council",
            "Type": "Organization",
            "Strong Match": ["British Council"],
            "Weak Match": [],
            "Description": "Organization that awarded Clara a scholarship.",
            "Summary": "Scholarship provider."
        }},
        {{
            "Name": "History of Art",
            "Type": "Field of Study",
            "Strong Match": ["History of Art"],
            "Weak Match": [],
            "Description": "Clara’s chosen academic discipline.",
            "Summary": "Field of study."
        }},
        {{
            "Name": "Dr. Martin Holloway",
            "Type": "Character",
            "Strong Match": ["Dr. Martin Holloway", "Martin Holloway"],
            "Weak Match": ["Professor Holloway"],
            "Description": "Clara’s first professor at the University of Sussex, who introduced her to archival work.",
            "Summary": "Important mentor figure."
        }},
        {{
            "Name": "Victoria and Albert Museum",
            "Type": "Place",
            "Strong Match": ["Victoria and Albert Museum"],
            "Weak Match": ["the Museum"],
            "Description": "Museum in London where Clara performed archival work.",
            "Summary": "Institution where Clara trained."
        }},
        {{
            "Name": "London",
            "Type": "Place",
            "Strong Match": ["London"],
            "Weak Match": [],
            "Description": "City in England where the Victoria and Albert Museum is located.",
            "Summary": "Location of museum."
        }},
        {{
            "Name": "Eleanor Whitcombe",
            "Type": "Character",
            "Strong Match": ["Eleanor Whitcombe"],
            "Weak Match": ["Whitcombe"],
            "Description": "Painter from the 19th century whose letters Clara uncovered.",
            "Summary": "Historical figure relevant to Clara’s research."
        }},
        {{
            "Name": "Royal Academy of Arts",
            "Type": "Organization",
            "Strong Match": ["Royal Academy of Arts"],
            "Weak Match": ["the Academy"],
            "Description": "Institution where Eleanor Whitcombe exhibited her paintings.",
            "Summary": "Art institution connected to Whitcombe."
        }},
        {{
            "Name": "October 1998",
            "Type": "Date/Event",
            "Strong Match": ["October 1998"],
            "Weak Match": [],
            "Description": "Time when Clara Mendoza moved from Seville to Brighton.",
            "Summary": "Key temporal marker for the narrative."
        }},
        {{
            "Name": "1872",
            "Type": "Date/Event",
            "Strong Match": ["1872"],
            "Weak Match": [],
            "Description": "Year in which Eleanor Whitcombe wrote the letters discovered by Clara.",
            "Summary": "Historical date relevant to archival discovery."
        }}
    ]
    </output>
    Prioritise finding as many entities as you can.

    Text: {text}
    """

    prompt = PromptTemplate(input_variables=["text"], template=template)

    message = HumanMessage(content=prompt.format(text=state["text"]))

    entities = llm.invoke([message]).strip()
    print(entities)

    # add unification with the database and entity class
    return {"entities": entities}
