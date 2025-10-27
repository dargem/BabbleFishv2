"""
Responsible for apis
"""


class NovelScraper:
    """
    Interfaces for apis that scrape novels
    Downloads scraped novels
    """

    def __init__(self, download_directory: str = "./data/raw"):
        self.download_directory = download_directory
