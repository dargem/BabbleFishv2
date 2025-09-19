"""Data models for books"""

from typing import Dict, List
import enum
from dataclasses import dataclass


@dataclass
class ChapterRequirement(enum):
    INGESTION = "Ingestion"
    TRANSLATION = "Translation"
    SUMMARY = "Summary"


class Chapter:
    """A singular chapter of a novel"""

    def __init__(self, original: str):
        self.original: str = original
        self.translation: str | None = None
        self.summary: str | None = None
        self.ingested_status: bool = False

    def get_requirements(self) -> List[ChapterRequirement]:
        """
        returns:
            List of enums representing required processing
        """
        checks = {
            ChapterRequirement.TRANSLATION: lambda c: c.translation is None,
            ChapterRequirement.SUMMARY: lambda c: c.summary is None,
            ChapterRequirement.INGESTION: lambda c: not c.ingested_status,
        }
        return [req for req, condition in checks.items() if condition(self)]


class Novel:
    """A novel contains chapters"""

    def __init__(
        self,
        chapters_dic: Dict[int:str] = {},
        loaded_chapter_dic: Dict[str:Chapter] = {},
    ):
        """
        Takes in and parses chapters

        Args:
            chapters: A list of chapters the novel has in strings, indexed by chapter idx starting at 0
        """
        self.chapters = loaded_chapter_dic
        for index, chapter_str in chapters_dic.keys():
            if index not in self.chapters:
                self.chapters[index] = Chapter(chapter_str)
