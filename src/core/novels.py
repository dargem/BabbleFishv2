"""Data models for books"""

from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass
from lingua import Language


class LanguageType(Enum):
    """Subset of lingua's Language objects"""

    ENGLISH = Language.ENGLISH
    CHINESE = Language.CHINESE
    JAPANESE = Language.JAPANESE
    KOREAN = Language.KOREAN
    SPANISH = Language.SPANISH
    FRENCH = Language.FRENCH


class Genre(Enum):
    ACTION = "Action"
    ADVENTURE = "Adventure"
    COMEDY = "Comedy"
    DRAMA = "Drama"
    FANTASY = "Fantasy"
    POST_APOCALYPTIC = "Post Apocalyptic"
    MAGICAL_REALISM = "Magical Realism"
    THRILLER = "Thriller"
    HISTORICAL = "Historical"
    HORROR = "Horror"
    MARTIAL_ARTS = "Martial Arts"
    MATURE = "Mature"
    MECHA = "Mecha"
    MYSTERY = "Mystery"
    PSYCHOLOGICAL = "Psychological"
    ROMANCE = "Romance"
    SCHOOL_LIFE = "School Life"
    SCI_FI = "Sci-Fi"
    SLICE_OF_LIFE = "Slice of Life"
    SPORTS = "Sports"
    SUPERNATURAL = "Supernatural"
    TRAGEDY = "Tragedy"
    WUXIA = "Wuxia"
    XIANXIA = "Xianxia"
    XUANHUAN = "Xuanhuan"
    DYSTOPIAN = "Dystopian"


class Requirement(Enum):
    # Novel Based
    STYLE_GUIDE = "Style Guide"
    GENRES = "Genres"
    LANGUAGE = "Language"
    # Chapter Based
    ANNOTATION = "Annotation"
    INGESTION = "Ingestion"
    TRANSLATION = "Translation"
    SUMMARY = "Summary"


@dataclass
class Chapter:
    """A singular chapter of a novel"""

    def __init__(self, original: str):
        self.original: str = original
        self.translation: str | None = None
        self.summary: str | None = None
        self.annotated_status: bool = False
        self.ingested_status: bool = False

    def get_requirements(self) -> List[Requirement]:
        """
        returns:
            List of enums representing required processing
        """
        # Insertion order is maintained in 3.7+, prioritises the first check first
        checks = {
            Requirement.SUMMARY: lambda c: c.summary is None,
            Requirement.INGESTION: lambda c: not c.ingested_status,
            Requirement.ANNOTATION: lambda c: not c.annotated_status,
            Requirement.TRANSLATION: lambda c: c.translation is None,
        }
        return [req for req, condition in checks.items() if condition(self)]


@dataclass
class Novel:
    """A novel contains chapters"""

    def __init__(self):
        self.indexed_chapters: Dict[int, Chapter] = {}
        self.style_guide: str = None
        self.genres: List[Genre] = None
        self.language: str = None

    def add_chapters(self, indexed_chapters: Dict[int, str]):
        """
        Converts incoming strings into chapter objects and adds to chapters

        Args:
            indexed_chapters: strings of chapters indexed by integer
        """
        indexed_chapters = self._filter_existing(indexed_chapters)

        # add the chapters, maybe should be done with dependency injection? feels fine to couple this tho
        for index, chapter_str in indexed_chapters.items():
            chapter = Chapter(original=chapter_str)
            self.indexed_chapters[index] = chapter

    def get_task(self) -> Tuple[int, str, Requirement] | None:
        """
        Identifies the next task needed for novel processing.

        Priority order:
        1. Novel-level requirements (style guide, genres, language) - these must be done first
        2. Chapter-level requirements (ingestion, translation) - done per chapter

        Returns:
            Tuple of (chapter_index, chapter_original_text, required_task)
            or None if no tasks are pending

            For novel-level requirements, chapter_index will be -1 to indicate it's novel-wide
        """

        # Check novel-level requirements first
        novel_requirements = self.get_novel_requirements()
        if novel_requirements:
            # Use first chapter text as sample for novel-level analysis
            if self.indexed_chapters:
                # Get the first chapter (by key order, not by assuming positive indices)
                first_chapter_idx = sorted(self.indexed_chapters.keys())[0]
                first_chapter_text = self.indexed_chapters[first_chapter_idx].original
                return (-1, first_chapter_text, novel_requirements[0])
            else:
                # No chapters loaded yet
                return None

        # Then check chapter-level requirements (sorted by chapter index for consistent ordering)
        for index in sorted(self.indexed_chapters.keys()):
            chapter = self.indexed_chapters[index]
            requirements = chapter.get_requirements()
            if requirements:
                # Return the first requirement found
                return (index, chapter.original, requirements[0])

        # No tasks pending
        return None

    def _filter_existing(self, indexed_chapters: Dict[int, str]) -> Dict[int, str]:
        """
        Filters out chapter indexes that are already existing in self.chapters

        Args:
            indexed_chapters: strings of chapters indexed by integer

        Returns:
            A dictionary of unique from stored chapter dictionary entries
        """
        new_chapters = {}
        for index, chapter_str in indexed_chapters.items():
            if index not in self.indexed_chapters:
                new_chapters[index] = chapter_str
        return new_chapters

    def get_novel_requirements(self) -> List[Requirement]:
        """
        Get the novel-level requirements (style guide, genres, language)

        Returns:
            List of novel-level requirements that are not yet completed
        """
        checks = {
            Requirement.STYLE_GUIDE: lambda n: n.style_guide is None,
            Requirement.GENRES: lambda n: n.genres is None,
            Requirement.LANGUAGE: lambda n: n.language is None,
        }
        return [req for req, condition in checks.items() if condition(self)]
