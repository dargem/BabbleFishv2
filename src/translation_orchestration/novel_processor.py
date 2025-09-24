from typing import List, Dict
from src.core import Novel


class NovelTranslator:
    """Orchestrator for the loose sequential translation process of a Novel object"""

    def __init__(self, novel: Novel = None):
        """
        Constructor with the option of preloading a past translation

        Args:
            novel: Optional preloaded novel object to continue translation on
        """
        if novel:
            self.novel = novel
        else:
            self.novel = Novel()  # maybe just do dependency injection of an empty novel? Probably better architecturally

    def add_chapters(self, indexed_chapters: Dict[int, str]):
        """
        Adds extra chapters to the novel object

        Args:
            indexed_chapters: strings of chapters indexed by integer
        """
        self.novel.add_chapters(indexed_chapters)

    def translate_book(chapters: List[str]) -> List[str]:
        """
        Translates a series of chapters sequentially
        """
