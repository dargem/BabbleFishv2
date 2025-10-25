"""Unit tests for utility functions."""

import unittest
from src.utils import parse_tagged_content, format_text_with_tags, reconstruct_text


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_parse_tagged_content_single_tag(self):
        """Test parsing single tagged content."""
        text = "<index 0>\nHello world\n</index 0>"
        result = parse_tagged_content(text)

        expected = {0: "Hello world"}
        self.assertEqual(result, expected)

    def test_parse_tagged_content_multiple_tags(self):
        """Test parsing multiple tagged content."""
        text = """
        <index 0>
        First paragraph
        </index 0>
        <index 2>
        Third paragraph
        </index 2>
        """
        result = parse_tagged_content(text)

        expected = {0: "First paragraph", 2: "Third paragraph"}
        self.assertEqual(result, expected)

    def test_parse_tagged_content_multiline(self):
        """Test parsing tagged content with multiple lines."""
        text = """<index 1>
        This is a longer text
        that spans multiple lines
        and should be preserved.
        </index 1>"""
        result = parse_tagged_content(text)

        expected_content = "This is a longer text\n        that spans multiple lines\n        and should be preserved."
        self.assertEqual(result[1], expected_content)

    def test_parse_tagged_content_empty(self):
        """Test parsing empty or invalid tagged content."""
        result = parse_tagged_content("")
        self.assertEqual(result, {})

        result = parse_tagged_content("No tags here")
        self.assertEqual(result, {})

    def test_format_text_with_tags_single_item(self):
        """Test formatting single text item with tags."""
        text_dict = {0: "Hello world"}
        result = format_text_with_tags(text_dict)

        self.assertIn("<index 0>", result)
        self.assertIn("Hello world", result)
        self.assertIn("</index 0>", result)

    def test_format_text_with_tags_multiple_items(self):
        """Test formatting multiple text items with tags."""
        text_dict = {0: "First paragraph", 2: "Third paragraph"}
        result = format_text_with_tags(text_dict)

        self.assertIn("<index 0>", result)
        self.assertIn("First paragraph", result)
        self.assertIn("</index 0>", result)
        self.assertIn("<index 2>", result)
        self.assertIn("Third paragraph", result)
        self.assertIn("</index 2>", result)

    def test_format_text_with_tags_empty(self):
        """Test formatting empty dictionary."""
        result = format_text_with_tags({})
        self.assertEqual(result, "")

    def test_reconstruct_text_single_paragraph(self):
        """Test reconstructing text from single paragraph."""
        text_dict = {0: "Hello world"}
        result = reconstruct_text(text_dict)

        self.assertEqual(result, "Hello world")

    def test_reconstruct_text_multiple_paragraphs(self):
        """Test reconstructing text from multiple paragraphs."""
        text_dict = {0: "First paragraph", 1: "Second paragraph", 2: "Third paragraph"}
        result = reconstruct_text(text_dict)

        expected = "First paragraph\n\nSecond paragraph\n\nThird paragraph"
        self.assertEqual(result, expected)

    def test_reconstruct_text_unordered_indices(self):
        """Test reconstructing text with unordered indices."""
        text_dict = {2: "Third paragraph", 0: "First paragraph", 1: "Second paragraph"}
        result = reconstruct_text(text_dict)

        expected = "First paragraph\n\nSecond paragraph\n\nThird paragraph"
        self.assertEqual(result, expected)

    def test_reconstruct_text_empty(self):
        """Test reconstructing from empty dictionary."""
        result = reconstruct_text({})
        self.assertEqual(result, "")

    def test_round_trip_processing(self):
        """Test that format -> parse -> reconstruct preserves content."""
        original_dict = {0: "First paragraph", 1: "Second paragraph"}

        # Format to tagged text
        tagged_text = format_text_with_tags(original_dict)

        # Parse back to dictionary
        parsed_dict = parse_tagged_content(tagged_text)

        # Reconstruct to final text
        final_text = reconstruct_text(parsed_dict)
        expected_text = reconstruct_text(original_dict)

        # Should match original structure
        self.assertEqual(final_text, expected_text)

    def test_parse_tagged_content_with_special_characters(self):
        """Test parsing tagged content with special characters."""
        text = '<index 0>\n"Hello," he said. "How are you?"\n</index 0>'
        result = parse_tagged_content(text)

        expected = {0: '"Hello," he said. "How are you?"'}
        self.assertEqual(result, expected)

    def test_format_text_preserves_whitespace(self):
        """Test that formatting preserves internal whitespace."""
        text_dict = {0: "Hello    world\n  with   spacing"}
        result = format_text_with_tags(text_dict)

        self.assertIn("Hello    world\n  with   spacing", result)


if __name__ == "__main__":
    unittest.main()
