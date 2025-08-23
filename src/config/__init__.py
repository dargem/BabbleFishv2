"""Configuration management for the translation system."""

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI

load_dotenv()


class Config:
    """Configuration class for the translation system."""

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY_3")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY_3 environment variable is required")

        # Set environment variable for Google API
        os.environ["GOOGLE_API_KEY"] = self.google_api_key

        # Model configuration
        self.model_name = "gemini-2.5-flash-lite"
        self.temperature = 0.7
        self.max_feedback_loops = 3

    def get_llm(self) -> GoogleGenerativeAI:
        """Get configured LLM instance."""
        return GoogleGenerativeAI(model=self.model_name, temperature=self.temperature)


# Global config instance
config = Config()
