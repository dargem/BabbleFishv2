"""entity addition node for the translation workflow, paired with the removal node"""

from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from ...models import TranslationState
from ...config import config


def term_addition_node(state: TranslationState) -> dict:
    """Recognise entities from original text.

    Args:
        state: Current translation state

    Returns:
        Dictionary with nodes + reasoning
    """
    print("Translating text...")

    llm = config.get_llm()

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
    
    This is an example input with example output.
    
    <input>
    In October 1998, Clara Mendoza moved from Seville, Spain, to Brighton, England, to begin her studies at the University of Sussex. 
    She had received a scholarship from the British Council to pursue a degree in History of Art. 
    Her first professor, Dr. Martin Holloway, introduced her to archival work at the Victoria and Albert Museum in London. 
    There, Clara uncovered letters written in 1872 by Eleanor Whitcombe, a painter who exhibited in the Royal Academy of Arts.
    </input>
    <output>
    [
        {
            "Name": "Clara",
            "Type": "Person",
            "Strong Match": [
            "Clara Mendoza"
            ],
            "Weak Match": []
        },
        {
            "Name": "Seville",
            "Type": "Location",
            "Strong Match": [
            "Seville, Spain"
            ],
            "Weak Match": []
        },
        {
            "Name": "Brighton",
            "Type": "Location",
            "Strong Match": [
            "Brighton, England"
            ],
            "Weak Match": []
        },
        {
            "Name": "University of Sussex",
            "Type": "Organization",
            "Strong Match": [],
            "Weak Match": []
        },
        {
            "Name": "British Council",
            "Type": "Organization",
            "Strong Match": [],
            "Weak Match": []
        },
        {
            "Name": "History of Art",
            "Type": "Field of Study",
            "Strong Match": [],
            "Weak Match": []
        },
        {
            "Name": "Martin Holloway",
            "Type": "Person",
            "Strong Match": [
            "Dr. Martin Holloway"
            ],
            "Weak Match": [
            "professor"
            ]
        },
        {
            "Name": "Victoria and Albert Museum",
            "Type": "Organization",
            "Strong Match": [],
            "Weak Match": []
        },
        {
            "Name": "London",
            "Type": "Location",
            "Strong Match": [],
            "Weak Match": []
        },
        {
            "Name": "1872",
            "Type": "Date",
            "Strong Match": [],
            "Weak Match": []
        },
        {
            "Name": "Eleanor Whitcombe",
            "Type": "Person",
            "Strong Match": [],
            "Weak Match": [
            "painter"
            ]
        },
        {
            "Name": "Royal Academy of Arts",
            "Type": "Organization",
            "Strong Match": [],
            "Weak Match": []
        }
    ]
    </output>
    Prioritise finding as many entities as you can.

    Text: {text}
    """

    prompt = PromptTemplate(input_variables=["text"], template=template)

    message = HumanMessage(content=prompt.format(text=state["text"]))

    entities = llm.invoke([message]).strip()

    # add unification with the database and entity class
    return {"entities": entities}