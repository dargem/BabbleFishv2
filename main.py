import os
from dotenv import load_dotenv
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image
load_dotenv()

# Set OpenAI API key
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY_3')

from langchain_google_genai import GoogleGenerativeAI

class State(TypedDict):
    text: str
    classification: str
    entities: List[str]
    summary: str
    sentiment: str

# Initialize the ChatOpenAI instance
llm = GoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

def classification_node(state: State):
    '''Classify the text into one of the categories: News, Blog, Research, or Other'''
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Classify the following text into one of the categories: News, Blog, Research, or Other.\n\nText:{text}\n\nCategory:"
    )
    message = HumanMessage(content=prompt.format(text=state["text"]))
    classification = llm.invoke([message]).strip()
    return {"classification": classification}

def entity_extraction_node(state: State):
    '''Extract all the entities (Person, Organization, Location) from the text'''
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Extract all the entities (Person, Organization, Location) from the following text. Provide the result as a comma-separated list.\n\nText:{text}\n\nEntities:"
    )
    message = HumanMessage(content=prompt.format(text=state["text"]))
    entities = llm.invoke([message]).strip().split(", ")
    return {"entities": entities}

def summarization_node(state: State):
    '''Summarize the text in one short sentence'''
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Summarize the following text in one short sentence.\n\nText:{text}\n\nSummary:"
    )
    message = HumanMessage(content=prompt.format(text=state["text"]))
    summary = llm.invoke([message]).strip()
    return {"summary": summary}

def sentiment_analysis_node(state: State):
    '''Finds the texts sentiment'''
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Summarize the sentiment of the following text as positive, neutral or negative.\n\nText:{text}\n\nSummary:"
    )
    message = HumanMessage(content=prompt.format(text=state["text"]))
    sentiment = llm.invoke([message]).strip()
    return {"sentiment": sentiment}

# Create our StateGraph
workflow = StateGraph(State)

# Add nodes to the graph
workflow.add_node("classification_node", classification_node)
workflow.add_node("entity_extraction", entity_extraction_node)
workflow.add_node("summarization", summarization_node)
workflow.add_node("sentiment_analysis", sentiment_analysis_node)

# Add edges to the graph
workflow.set_entry_point("classification_node")  # Set the entry point of the graph
workflow.add_edge("classification_node", "entity_extraction")
workflow.add_edge("entity_extraction", "summarization")
workflow.add_edge("summarization", "sentiment_analysis")
workflow.add_edge("sentiment_analysis", END)

# Compile the graph
app = workflow.compile()


class EnhancedState(TypedDict):
    text: str
    classification: str
    entities: List[str]
    summary: str
    sentiment: str

def route_after_classification(state: EnhancedState) -> str:
    category = state["classification"].lower()
    return category in ["news", "research"] # returns true when one of these, else false
# a conditional workflow also
conditional_workflow = StateGraph(EnhancedState)

# Add nodes
conditional_workflow.add_node("classification_node", classification_node)
conditional_workflow.add_node("entity_extraction", entity_extraction_node)
conditional_workflow.add_node("summarization", summarization_node)
conditional_workflow.add_node("sentiment_analysis", sentiment_analysis_node)

# Set entry point
conditional_workflow.set_entry_point("classification_node")

# Add conditional edge
conditional_workflow.add_conditional_edges("classification_node", route_after_classification, path_map={
    True: "entity_extraction",
    False: "summarization"
})

# Add remaining static edges
conditional_workflow.add_edge("entity_extraction", "summarization")
conditional_workflow.add_edge("summarization", "sentiment_analysis")
conditional_workflow.add_edge("sentiment_analysis", END)

# Compile
conditional_app = conditional_workflow.compile()


# Creates code for a mermaid visualisation
try:
    mermaid_code = conditional_app.get_graph().draw_mermaid()
    md_content = f"""# Workflow Graph\n\n```mermaid\n{mermaid_code}\n```\n"""
    with open("workflow_graph.md", "w") as f:
        f.write(md_content)
except Exception as e:
    print(f"Error generating Mermaid diagram: {e}")

# Test the setup
#response = llm.invoke("Hello! Are you working?")
#print(response)

sample_text = """
Here's what I learned from a week of meditating in silence. No phones, no talking—just me, my breath, and some deep realizations.
"""
state_input = {"text": sample_text}
result = conditional_app.invoke(state_input)

print("Classification:", result["classification"])
print("\nEntities:", result.get("entities","skipped"))
print("\nSummary:", result["summary"])
print("\nSentiment:", result["sentiment"])

