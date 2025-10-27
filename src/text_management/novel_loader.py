"""
Responsible for loading novels from files
"""

from src.core import Novel


class NovelLoader:
    def __init__(self, download_directory: str = "./data/raw"):
        self.download_directory = download_directory

    def get_novel(self) -> Novel:
        """
        Returns:
            Novel object
        """
