"""Utility functions for the translation system."""

import re
from typing import Dict, Any


def parse_tagged_content(text: str) -> Dict[int, str]:
    """Parse content from tagged text format.

    Args:
        text: Text containing <index N>...</index N> tags

    Returns:
        Dictionary mapping index numbers to content
    """
    pattern = r"<index (\d+)>\s*(.*?)\s*</index \1>"
    matches = re.findall(pattern, text, re.DOTALL)
    return {int(idx): content for idx, content in matches}


def format_text_with_tags(text_dict: Dict[int, str]) -> str:
    """Format dictionary of text into tagged format.

    Args:
        text_dict: Dictionary mapping indices to text content

    Returns:
        Formatted string with index tags
    """
    formatted_text = ""
    for i, text in text_dict.items():
        formatted_text += f"""
        <index {i}>
        {text}
        </index {i}>
        """
    return formatted_text


def reconstruct_text(text_dict: Dict[int, str]) -> str:
    """Reconstruct full text from indexed dictionary.

    Args:
        text_dict: Dictionary mapping indices to text content

    Returns:
        Reconstructed text with paragraphs separated by double newlines
    """
    result = ""
    for key in sorted(text_dict.keys()):
        result += text_dict[key] + "\n\n"
    return result.rstrip("\n\n")
