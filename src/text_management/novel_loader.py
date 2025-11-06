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

    def get_sample_novel(self):
        """
        
        Returns:
            Sample novel object
        """
        with open("data/raw/novel_7550580137809431576", "r") as f:
            file = f.read()

