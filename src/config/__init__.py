"""Configuration management for the translation system."""

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
import enum

load_dotenv()

"""
model list

gemini-2.5-pro
gemini-2.5-flash
gemini-2.5-flash-lite
gemini-2.0-flash
gemini-2.0-flash-lite

gemini-2.5-flash-lite-preview-06-17
gemini-live-2.5-flash-preview

"""


class Config:
    """Configuration class for the translation system."""

    def __init__(self):
        # Set environment variable for Google API
        self.key_usage_dic = {
            value: 0 for (key, value) in os.environ.items() if "GOOGLE_API_KEY" in key
        }
        if not self.key_usage_dic:
            raise ValueError("No environmental variables set for API Key, failing")

        # Model configuration
        self.model_name = "gemini-2.5-flash-lite"
        self.temperature = 0.7
        self.max_feedback_loops = 3

    def _next_api_key(self):
        lowest_entry = None
        for key, value in self.key_usage_dic.items():
            if not lowest_entry:
                lowest_entry = (key, value)

            if value < lowest_entry[1]:
                lowest_entry = (key, value)
        return lowest_entry[0]

    def get_llm(self) -> GoogleGenerativeAI:
        """Get configured LLM instance."""
        os.environ["GOOGLE_API_KEY"] = self._next_api_key()
        self.key_usage_dic[os.environ["GOOGLE_API_KEY"]] += 1  # tick it
        return GoogleGenerativeAI(model=self.model_name, temperature=self.temperature)


# Global config instance
config = Config()