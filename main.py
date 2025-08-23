import os
from dotenv import load_dotenv
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image
import re

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY_3")

from langchain_google_genai import GoogleGenerativeAI


class TranslationState(TypedDict):
    text: str
    language: str
    translation: str
    fluent_translation: str
    feedback: str
    feedback_rout_loops: int


llm = GoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.7)


def language_detector_node(state: TranslationState):
    print("detecting language...")
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        Detect the language of the following, outputting one word.
        Text:{text}
        Summary:"
        """,
    )
    message = HumanMessage(content=prompt.format(text=state["text"]))
    language = llm.invoke([message]).strip()
    return {"language": language}


def translator_node(state: TranslationState):
    print("translating text...")

    template = """
    You are a professional translator specialising in fiction. 
    You work with Chinese to English translations and are highly proficient in localisation.
    Prioritise fluency while maintaining semantic meaning.
    Translate the following {language} text to English.
    Text: {text}
    """
    if "translation" in state:
        template += """
        Your prior translation was: 
        {translation}
        Your feedback was: 
        {feedback}
        With this feedback incorporated, create a richer response.
        Your updated translation, incorporating feedback:
        """
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
        # print(state["feedback"])
    else:
        template += "\n\n Translation:"
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


def inc_translate_feedback_node(state: TranslationState) -> TranslationState:
    if "feedback_rout_loops" not in state:
        state["feedback_rout_loops"] = 0
    state["feedback_rout_loops"] += 1
    return state


def junior_editor_node(state: TranslationState):
    print("junior editoring...")
    prompt = PromptTemplate(
        input_variables=["text", "translation"],
        template="""
        Evaluate the quality of the following translation for the text.
        Be highly critical in your evaluation, you only want the very best.
        Be harsh but reasonable.
        If it is of high enough quality return the words /"approved response accepted/", review by the following:
        - readability
        - fluency
        - reading level
        - consistency of terminology
        - semantic accuracy
        Produce a list of specific errors/suggestions with justifications and avoid a general conclusion.
        Original Text: {text}
        Translation for assessment: {translation}
        """,
    )
    message = HumanMessage(
        content=prompt.format(translation=state["translation"], text=state["text"])
    )
    feedback = llm.invoke([message]).strip()
    return {"feedback": feedback}


def fluency_editor_node(state: TranslationState):
    """edits the translation text through proofreading"""
    print("aiding fluency...")
    split_text = state["translation"].split("\n\n")
    keyed_text = {edit_index: text for edit_index, text in enumerate(split_text)}
    tag_formatted_input = ""
    for i, text in keyed_text.items():
        tag_formatted_input += f"""
        <index {i}>
        {text}
        </index {i}>
        """
    # potentially input a created style guide also
    # potentially add null output option
    prompt = PromptTemplate(
        template=f"""
        You are a professional proofreader. 
        Your job is to read for rhythm, voice, and narrative flow.
        You'll focus on the lyrical quality of the prose, ensuring the story unfolds with a natural, compelling pace.
        You will refine sentence structure, word choice, and aesthetics of form to enhance the reader's immersion in the world the author has built.
        You will make sure the author's voice is consistent and strong, and that every word serves the story without disrupting the narrative's pulse.
        Create as many improvements as you can. 
        
        The text is divided into paragraphs inside <index N> ... </index N> tags.  
        For any index where you see room for improvement, output ONLY the improved version inside the same tags.  
        Do not output unchanged indices. Do not add explanations or commentary.  
        It is acceptable to split a long sentence into multiple sentences inside an index if it improves clarity.  
        
        Example:
        Input:
        <index 5>
        He placed the card upon the desk and once again closed his eyes, silently reciting in his heart a prayer.
        </index 5>

        Output:
        <index 5>
        Placing the card upon the desk, he closed his eyes once more, silently reciting a prayer in his heart.
        </index 5>

        
        The input of tagged text for proofreading is below, output in formatting described above:
        {tag_formatted_input}
        """
    )
    # don't have any reference to states for now
    message = HumanMessage(content=prompt.format())
    unparsed_fluency_fixed_text = llm.invoke([message])
    pattern = r"<index (\d+)>\s*(.*?)\s*</index \1>"
    matches = re.findall(pattern, unparsed_fluency_fixed_text, re.DOTALL)
    for idx, content in matches:
        # then overwrite using the new parser
        keyed_text[int(idx)] = content
    fluency_processed_text = ""
    for key in keyed_text:
        fluency_processed_text += keyed_text[key] + "\n\n"
    return {"fluent_translation": fluency_processed_text}


# conditional logic
def route_junior_pass(state: TranslationState) -> bool:
    return "approved response accepted" in state["feedback"]


def rout_increment_exceed(state: TranslationState) -> bool:
    """If its past the max number of feedback loops, skip the junior editor"""
    return state["feedback_rout_loops"] >= 3


# creating the graph
workflow = StateGraph(TranslationState)
workflow.add_node("language_detector_node", language_detector_node)
workflow.add_node("translator_node", translator_node)
workflow.add_node("junior_editor_node", junior_editor_node)
workflow.add_node("inc_translate_feedback_node", inc_translate_feedback_node)
workflow.add_node("fluency_editor_node", fluency_editor_node)

workflow.set_entry_point("language_detector_node")
workflow.add_edge("language_detector_node", "translator_node")
workflow.add_edge("translator_node", "inc_translate_feedback_node")
workflow.add_conditional_edges(
    "inc_translate_feedback_node",
    rout_increment_exceed,
    path_map={True: "fluency_editor_node", False: "junior_editor_node"},
)

workflow.add_conditional_edges(
    "junior_editor_node",
    route_junior_pass,
    path_map={True: "fluency_editor_node", False: "translator_node"},
)

workflow.add_edge("fluency_editor_node", END)
app = workflow.compile()

if __name__ == "__main__":
    sample_text = """
    夏日的黄昏，微风吹拂着窗帘，带来一丝丝晚香玉的甜味。我坐在书桌前，摊开一本旧书，但思绪早已飘到了窗外。天边，火烧云如同被打翻的颜料盒，将整个天空染成绚烂的橘红、深紫和金黄。城市的喧嚣在此刻变得遥远而模糊，只剩下蝉鸣声声，仿佛在诉说着一个古老而漫长的故事。

    我抬头望向书架，那本尘封已久的日记本静静地躺在那里。它曾记录着我的青春、梦想和那些早已淡忘的面孔。每一页都像是一扇通往过去的门，门后是阳光明媚的校园、无忧无虑的笑声和那个曾经的自己。我犹豫着，最终还是伸出手，指尖触碰到粗糙的封面，一股冰冷的、熟悉的感觉涌上心头。

    记忆的河流开始缓缓流淌，带着我回到了那个炎热的午后。那时，我们坐在梧桐树下，他用指尖在沙地上勾勒着未来的蓝图。他的眼神里充满了光芒，而我只是静静地听着，感受着那份属于年轻人的热烈与憧憬。一切都如此真实，仿佛昨日重现。我闭上眼睛，试图抓住那份温度，但当再次睁开时，眼前只剩下了书桌上微弱的台灯光芒和窗外渐渐黯淡的夜色。
    """
    with open("data/raw/lotm_files/lotm1.txt", "r", encoding="UTF-8") as f:
        sample_text = f.read()
    state_input = {"text": sample_text}
    result = app.invoke(state_input)
    for key in [
        string_key for string_key in result if isinstance(result[string_key], str)
    ]:
        print(key + " " + result[key])
