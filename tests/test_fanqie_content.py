import pytest

from src.text_management.lightnovel_crawler import FanqieNovelDownloader


@pytest.mark.parametrize(
    "content_data, expected",
    [
        (
            {"content": "<p>First sentence.<br/>Still first.</p><p>Second para</p>"},
            "First sentence. Still first.\n\nSecond para",
        ),
        (
            {
                "content": "Line one that wraps\ncontinues here\n\nAnother paragraph",
            },
            "Line one that wraps continues here\n\nAnother paragraph",
        ),
        (
            {"content_paragraphs": ["第一段第一行", "第二段"]},
            "第一段第一行\n\n第二段",
        ),
    ],
)
def test_format_chapter_content(content_data, expected):
    formatted = FanqieNovelDownloader._format_chapter_content(content_data)
    assert formatted == expected
