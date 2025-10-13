"""Text loader that integrates fanqie-novel-downloader with Novel objects."""

import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

from .lightnovel_crawler import (
    FanqieNovelDownloader,
    FanqieConfig,
    OutputFormat,
    download_fanqie_novel,
    download_from_fanqie_url
)
from src.core import Novel


logger = logging.getLogger(__name__)


class NovelTextLoader:
    """High-level interface for loading text into Novel objects from Fanqie novels and files"""
    
    def __init__(self, download_dir: str = "./data/raw"):
        """
        Initialize the text loader
        
        Args:
            download_dir: Directory for downloaded novels
        """
        self.download_dir = download_dir
        self.downloader = FanqieNovelDownloader(download_dir)
        
        # Ensure download directory exists
        os.makedirs(download_dir, exist_ok=True)
    
    def load_from_fanqie_url(
        self,
        fanqie_url: str,
        novel: Optional[Novel] = None,
        chapter_limit: Optional[int] = None,
        force_redownload: bool = False
    ) -> Novel:
        """
        Load a novel from a Fanqie novel URL
        
        Args:
            fanqie_url: URL of the Fanqie novel page
            novel: Existing Novel object to load into (creates new if None)
            chapter_limit: Maximum number of chapters to download
            force_redownload: Whether to redownload if already exists
            
        Returns:
            Novel object with loaded chapters
        """
        if novel is None:
            novel = Novel()
        
        # Extract novel ID from URL
        novel_id = self.downloader.extract_novel_id_from_url(fanqie_url)
        if not novel_id:
            raise ValueError(f"Could not extract novel ID from URL: {fanqie_url}")
        
        return self.load_from_fanqie_id(novel_id, novel, chapter_limit, force_redownload)
    
    def load_from_fanqie_id(
        self,
        novel_id: str,
        novel: Optional[Novel] = None,
        chapter_limit: Optional[int] = None,
        force_redownload: bool = False
    ) -> Novel:
        """
        Load a novel from a Fanqie novel ID
        
        Args:
            novel_id: Fanqie novel ID
            novel: Existing Novel object to load into (creates new if None)
            chapter_limit: Maximum number of chapters to download
            force_redownload: Whether to redownload if already exists
            
        Returns:
            Novel object with loaded chapters
        """
        if novel is None:
            novel = Novel()
        
        # Configure download
        config = FanqieConfig(
            novel_id=novel_id,
            output_path=self.download_dir,
            format_type=OutputFormat.TXT,
            end_chapter=chapter_limit
        )
        
        # Download the novel
        logger.info("Downloading novel from Fanqie ID: %s", novel_id)
        result = self.downloader.download_novel(config)
        
        if not result["success"]:
            raise RuntimeError(f"Failed to download novel: {result.get('error', 'Unknown error')}")
        
        # Load chapters into the novel
        chapter_files = result["chapter_files"]
        
        if not chapter_files:
            raise RuntimeError("No chapters were downloaded")
        
        # Load chapters from downloaded files
        chapters = self._load_chapters_from_files([Path(f) for f in chapter_files])
        novel.add_chapters(chapters)
        
        logger.info("Successfully loaded %d chapters into novel", len(chapters))
        return novel
    
    def search_and_load_fanqie(
        self,
        query: str,
        novel: Optional[Novel] = None,
        chapter_limit: int = 10,
        novel_index: int = 0
    ) -> Novel:
        """
        Search for a novel on Fanqie and load it automatically
        
        Args:
            query: Search query
            novel: Existing Novel object to load into (creates new if None)
            chapter_limit: Number of chapters to download
            novel_index: Index of novel to select from search results (0 = first)
            
        Returns:
            Novel object with loaded chapters
        """
        if novel is None:
            novel = Novel()
        
        # Search for novels
        search_results = self.downloader.search_novels(query)
        
        if "error" in search_results:
            raise RuntimeError(f"Search failed: {search_results['error']}")
        
        # Extract novel IDs from search results
        # This would need to be implemented based on the actual API response format
        novels_data = search_results.get("data", [])
        if not novels_data:
            raise RuntimeError("No novels found in search results")
        
        if novel_index >= len(novels_data):
            raise RuntimeError(f"Novel index {novel_index} out of range (found {len(novels_data)} novels)")
        
        # Get the selected novel
        selected_novel = novels_data[novel_index]
        novel_id = selected_novel.get("id") or selected_novel.get("novel_id")
        
        if not novel_id:
            raise RuntimeError("Could not extract novel ID from search results")
        
        # Download and load the novel
        return self.load_from_fanqie_id(novel_id, novel, chapter_limit)
    
    def load_from_directory(
        self,
        directory_path: str,
        novel: Optional[Novel] = None,
        file_pattern: str = "*.txt"
    ) -> Novel:
        """
        Load a novel from existing text files in a directory
        
        Args:
            directory_path: Path to directory containing text files
            novel: Existing Novel object to load into (creates new if None)
            file_pattern: Pattern to match text files
            
        Returns:
            Novel object with loaded chapters
        """
        if novel is None:
            novel = Novel()
        
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find text files
        text_files = list(directory.glob(file_pattern))
        text_files.sort()  # Sort for consistent ordering
        
        if not text_files:
            raise RuntimeError(f"No files matching pattern '{file_pattern}' found in {directory_path}")
        
        # Load chapters
        chapters = self._load_chapters_from_files(text_files)
        novel.add_chapters(chapters)
        
        logger.info("Loaded %d chapters from directory: %s", len(chapters), directory_path)
        return novel
    
    def load_from_single_file(
        self,
        file_path: str,
        novel: Optional[Novel] = None,
        chapter_separator: str = "\n\n\n"
    ) -> Novel:
        """
        Load a novel from a single text file, splitting into chapters
        
        Args:
            file_path: Path to the text file
            novel: Existing Novel object to load into (creates new if None)
            chapter_separator: String that separates chapters
            
        Returns:
            Novel object with loaded chapters
        """
        if novel is None:
            novel = Novel()
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read the entire file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chapters
        chapter_texts = content.split(chapter_separator)
        chapter_texts = [text.strip() for text in chapter_texts if text.strip()]
        
        # Create indexed chapters
        chapters = {i + 1: text for i, text in enumerate(chapter_texts)}
        novel.add_chapters(chapters)
        
        logger.info("Loaded %d chapters from file: %s", len(chapters), file_path)
        return novel
    
    def _load_chapters_from_files(self, file_paths: List[Path]) -> Dict[int, str]:
        """
        Load chapter text from a list of files
        
        Args:
            file_paths: List of file paths to load
            
        Returns:
            Dictionary mapping chapter index to chapter text
        """
        chapters = {}
        
        for i, file_path in enumerate(file_paths):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:  # Only add non-empty chapters
                    chapters[i + 1] = content
                    
            except Exception as e:
                logger.warning("Failed to load file %s: %s", file_path, e)
                continue
        
        return chapters
    
    def get_downloaded_novels(self) -> List[str]:
        """
        Get list of already downloaded novels
        
        Returns:
            List of novel directory names
        """
        return self.downloader.list_downloaded_novels()
    
    def get_novel_info(self, novel_id: str) -> Dict:
        """
        Get information about a Fanqie novel without downloading
        
        Args:
            novel_id: Fanqie novel ID
            
        Returns:
            Dictionary with novel information
        """
        return self.downloader.get_novel_info(novel_id)
    
    def search_fanqie_novels(self, query: str) -> Dict:
        """
        Search for novels on Fanqie platform
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        return self.downloader.search_novels(query)


# Convenience functions for quick novel loading

def load_novel_from_fanqie_url(
    fanqie_url: str,
    download_dir: Optional[str] = None,
    chapter_limit: Optional[int] = None
) -> Novel:
    """
    Quick function to load a novel from a Fanqie URL
    
    Args:
        fanqie_url: URL of the Fanqie novel page
        download_dir: Directory for downloads
        chapter_limit: Maximum chapters to download
        
    Returns:
        Novel object with loaded chapters
    """
    if download_dir is None:
        repo_root = Path(__file__).resolve().parents[2]
        download_dir = str(repo_root / "data" / "raw")

    loader = NovelTextLoader(download_dir)
    return loader.load_from_fanqie_url(fanqie_url, chapter_limit=chapter_limit)


def load_novel_from_fanqie_id(
    novel_id: str,
    download_dir: Optional[str] = None,
    chapter_limit: Optional[int] = None
) -> Novel:
    """
    Quick function to load a novel from a Fanqie novel ID
    
    Args:
        novel_id: Fanqie novel ID
        download_dir: Directory for downloads
        chapter_limit: Maximum chapters to download
        
    Returns:
        Novel object with loaded chapters
    """
    if download_dir is None:
        repo_root = Path(__file__).resolve().parents[2]
        download_dir = str(repo_root / "data" / "raw")

    loader = NovelTextLoader(download_dir)
    return loader.load_from_fanqie_id(novel_id, chapter_limit=chapter_limit)


def search_and_load_fanqie_novel(
    query: str,
    download_dir: Optional[str] = None,
    chapter_limit: int = 10,
    novel_index: int = 0
) -> Novel:
    """
    Quick function to search and load a Fanqie novel
    
    Args:
        query: Search query
        download_dir: Directory for downloads
        chapter_limit: Number of chapters to download
        novel_index: Index of novel to select from results
        
    Returns:
        Novel object with loaded chapters
    """
    if download_dir is None:
        repo_root = Path(__file__).resolve().parents[2]
        download_dir = str(repo_root / "data" / "raw")

    loader = NovelTextLoader(download_dir)
    return loader.search_and_load_fanqie(query, chapter_limit=chapter_limit, novel_index=novel_index)