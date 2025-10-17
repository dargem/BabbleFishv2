from pydantic import BaseModel, Field, field_validator
from typing import List, Dict
from src.core import Genre
from src.providers import LLMProvider
from src.workflows import SetupState
from textwrap import dedent
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate

class GenreSchema(BaseModel):
    """Pydantic schema for a list of genres"""

    genre_list: List[Genre] = Field(..., description="A list of genres for choice, USE ONLY THESE NOTHING ELSE")
    @field_validator("genre_list", mode="before")
    @classmethod
    def standardize_case(cls, value: List[str]) -> List[str]:
        """Converts all incoming genre strings to uppercase before validation."""
        if not isinstance(value, list):
            return value  # Let Pydantic handle the wrong type error
        return [g.title() for g in value if isinstance(g, str)]


class GenreDetector:
    """Detects the genre of a text"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def find_genres(self, state: SetupState) -> Dict[str, List[Genre]]:
        """
        Finds the genres of the novel

        Args:
            state: Current setup state, only needs text str

        Returns:
            A list of genre enum members it classifies the book as having, in form of a dict entry
        """

        template = dedent("""
        You are an experienced text annotator.
        Your task is to classify chapters from the following text according to a list of provided Genres.
                          
        === The text to classify ===
        {text}
                          
        === Your response below ===
        """)

        prompt = PromptTemplate(input_variable=["text"], template=template)

        message = HumanMessage(content=prompt.format(text=state["text"]))

        genres: GenreSchema = await self.llm_provider.schema_invoke(
            [message], schema=GenreSchema
        )

        return {"genres": genres.genre_list}
