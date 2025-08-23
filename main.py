import os
from dotenv import load_dotenv
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY_3")

from langchain_google_genai import GoogleGenerativeAI


class TranslationState(TypedDict):
    text: str
    language: str
    translation: str
    feedback: str


llm = GoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)


def language_detector_node(state: TranslationState):
    print("detecting language...")
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Detect the language of the following, outputting one word.\n\nText:{text}\n\nSummary:",
    )
    message = HumanMessage(content=prompt.format(text=state["text"]))
    language = llm.invoke([message]).strip()
    return {"language": language}


def translator_node(state: TranslationState):
    print("translating text...")

    template = "Translate the following {language} text to English.\n\nText:{text}"
    if "translation" in state:
        template += "\n\nYour prior translation was {translation}"
        template += "\n\nYour feedback was {feedback}"
        template += "\n\nYour updated translation:"
        prompt = PromptTemplate(
            input_variables=["text", "language", "feedback", "translation"],
            template=template,
        )
        message = HumanMessage(
            content=prompt.format(
                language=state["language"],
                text=state["text"],
                feedback=state["feedback"],
                translation=state["translation"],
            )
        )
        print(state["feedback"])
    else:
        template+= "\n\n Translation:"
        prompt = PromptTemplate(
            input_variables=["text", "language"],
            template=template,
        )
        message = HumanMessage(
            content=prompt.format(
                language=state["language"],
                text=state["text"],
            )
        )
    translation = llm.invoke([message]).strip()
    return {"translation": translation}


def junior_editor_node(state: TranslationState):
    print("junior editoring...")
    prompt = PromptTemplate(
        input_variables=["text", "translation"],
        template="""
        Evaluate the quality of the following translation for the text.
        Be highly critical in your evaluation, you only want the very best.
        If it is of high enough quality return the word \"approved response\" in your response else give feedback for improvement.
        Text: {text}
        Translation: {translation}
        """,
    )
    message = HumanMessage(
        content=prompt.format(translation=state["translation"], text=state["text"])
    )
    feedback = llm.invoke([message]).strip()
    return {"feedback": feedback}


# conditional logic
def route_junior_check(state: TranslationState) -> bool:
    return "approved response" in state["feedback"]


# creating the graph
workflow = StateGraph(TranslationState)
workflow.add_node("language_detector_node", language_detector_node)
workflow.add_node("translator_node", translator_node)
workflow.add_node("junior_editor_node", junior_editor_node)

workflow.set_entry_point("language_detector_node")
workflow.add_edge("language_detector_node", "translator_node")
workflow.add_edge("translator_node", "junior_editor_node")
workflow.add_conditional_edges(
    "junior_editor_node",
    route_junior_check,
    path_map={True: END, False: "translator_node"},
)
app = workflow.compile()

if __name__ == "__main__":
    sample_text = """
    道可道，非常道；名可名，非常名。
    无名，天地之始；有名，万物之母。
    故常无，欲以观其妙；常有，欲以观其徼。
    此两者，同出而异名，同谓之玄。
    玄之又玄，众妙之门。
    """
    state_input = {"text": sample_text}
    result = app.invoke(state_input)
    for key in result:
        print(key + " " + result[key])
