"""Configuration management for the translation system."""

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
import enum
import re
import textwrap
from typing import Dict

load_dotenv(override=True)  # Force override system environment variables

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
        # Model configuration
        self.model_name = "gemini-2.5-flash-lite"
        self.temperature = 0.7
        self.max_feedback_loops = 3

        # Set environment variable for Google API
        self.key_usage_dic = {
            value: 0
            for (key, value) in os.environ.items()
            if "GOOGLE_API_KEY" in key and self._health_check(value)
        }

        if not self.key_usage_dic:
            raise ValueError("No environmental variables set for API Key, failing")

    def _health_check(self, api_key):
        """Does a query to check the keys actually working"""
        os.environ["GOOGLE_API_KEY"] = api_key
        llm = GoogleGenerativeAI(model=self.model_name, temperature=self.temperature)
        try:
            # llm.invoke("Hey are you working, repond with yes/no")
            holder = 0
        except Exception as e:
            e = str(e)
            match = re.search(r'message:\s*"([^"]+)"', e)
            if match:
                raise Exception(
                    textwrap.dedent(f"""
                Error Message:
                {match.group(1)}
                With API KEY:
                {api_key}
                """)
                )
            else:
                raise Exception(
                    textwrap.dedent(f"""
                {e}
                Error with API key:
                {api_key}
                Additionally the parser failed
                """)
                )
        print("key healthy")
        return True

    def _next_api_key(self):
        lowest_entry = None
        for key, value in self.key_usage_dic.items():
            if not lowest_entry:
                lowest_entry = (key, value)

            if value < lowest_entry[1]:
                lowest_entry = (key, value)
        return lowest_entry[0]

    def get_llm(self, force_rotate=False, schema: Dict=None) -> GoogleGenerativeAI:
        """Get configured LLM instance."""
        if force_rotate or self.key_usage_dic[os.environ["GOOGLE_API_KEY"]] > 15:
            os.environ["GOOGLE_API_KEY"] = self._next_api_key()
        self.key_usage_dic[os.environ["GOOGLE_API_KEY"]] += 1  # tick it
        if not schema:
            return GoogleGenerativeAI(model=self.model_name, temperature=self.temperature)
        return GoogleGenerativeAI(model=self.model_name, temperature=self.temperature).with_structured_output(schema)


# Global config instance
config = Config()
