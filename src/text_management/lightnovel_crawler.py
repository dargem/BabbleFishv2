"""Interface for Fanqie-novel-Downloader tool integration."""

import subprocess
import logging
import json
import os
import re
import requests
from typing import List, Dict, Optional, Union, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from html import unescape


logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Supported output formats for fanqie-novel-downloader"""
    TXT = "1"
    EPUB = "2"


@dataclass
class FanqieConfig:
    """Configuration for fanqie-novel-downloader execution"""
    novel_id: Optional[str] = None
    search_query: Optional[str] = None
    output_path: Optional[str] = None
    format_type: OutputFormat = OutputFormat.TXT
    start_chapter: Optional[int] = None
    end_chapter: Optional[int] = None
    
    # API configuration
    max_workers: int = 4
    max_retries: int = 3
    request_timeout: int = 15
    request_rate_limit: float = 0.4
    download_enabled: bool = True


class FanqieDownloaderError(Exception):
    """Custom exception for fanqie-novel-downloader errors"""
    pass


class FanqieAPI:
    """Direct API interface for Fanqie novels"""
    
    BASE_URL = "https://api-return.cflin.ddns-ip.net/api/xiaoshuo/fanqie"
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        # Set a proper user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_novels(self, query: str) -> Dict:
        """
        Search for novels by title
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        try:
            response = self.session.get(
                self.BASE_URL,
                params={"q": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Search failed: %s", e)
            return {"error": str(e)}
    
    def get_novel_details(self, novel_id: str) -> Dict:
        """
        Get novel details by ID
        
        Args:
            novel_id: Novel ID from Fanqie platform
            
        Returns:
            Dictionary with novel details
        """
        try:
            response = self.session.get(
                self.BASE_URL,
                params={"xq": novel_id},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get novel details: %s", e)
            return {"error": str(e)}
    
    def get_chapter_list(self, novel_id: str) -> Dict:
        """
        Get chapter list for a novel
        
        Args:
            novel_id: Novel ID from Fanqie platform
            
        Returns:
            Dictionary with chapter list
        """
        try:
            response = self.session.get(
                self.BASE_URL,
                params={"mulu": novel_id},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get chapter list: %s", e)
            return {"error": str(e)}
    
    def get_chapter_content(self, chapter_id: str) -> Dict:
        """
        Get content for a specific chapter
        
        Args:
            chapter_id: Chapter ID from Fanqie platform
            
        Returns:
            Dictionary with chapter content
        """
        try:
            response = self.session.get(
                self.BASE_URL,
                params={"content": chapter_id},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get chapter content: %s", e)
            return {"error": str(e)}


class FanqieNovelDownloader:
    """Python interface for fanqie-novel-downloader"""
    
    def __init__(self, default_output_dir: Optional[str] = None):
        """
        Initialize the downloader interface

        Args:
            default_output_dir: Default directory for downloads. If None, will resolve
                to the repository root's `data/raw` directory so downloads are
                always placed outside `src/` regardless of cwd.
        """
        # Resolve repository root (project root) based on this file's location:
        repo_root = Path(__file__).resolve().parents[2]
        default_data_dir = repo_root / "data" / "raw"

        # Use provided path or repo-root data/raw
        self.default_output_dir = str(Path(default_output_dir) if default_output_dir else default_data_dir)
        self.api = FanqieAPI()
        self._verify_installation()
    
    def _verify_installation(self) -> bool:
        """
        Check if we can access the Fanqie API
        
        Returns:
            True if accessible, raises exception if not
        """
        try:
            # Test the API with a simple request
            response = requests.get(
                self.api.BASE_URL,
                params={"q": "test"},
                timeout=5
            )
            if response.status_code == 200:
                logger.info("Fanqie API is accessible")
                return True
            else:
                raise FanqieDownloaderError("Fanqie API is not accessible")
        except requests.RequestException as e:
            raise FanqieDownloaderError(f"Cannot access Fanqie API: {e}")
    
    def search_novels(self, query: str) -> Dict:
        """
        Search for novels using a query string
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        logger.info("Searching for novels with query: %s", query)
        return self.api.search_novels(query)
    
    def get_novel_info(self, novel_id: str) -> Dict:
        """
        Get detailed information about a novel
        
        Args:
            novel_id: Novel ID from Fanqie platform
            
        Returns:
            Dictionary with novel information
        """
        logger.info("Getting novel info for ID: %s", novel_id)
        
        # Get novel details
        novel_details = self.api.get_novel_details(novel_id)
        if "error" in novel_details:
            return novel_details
        
        # Get chapter list
        chapter_list = self.api.get_chapter_list(novel_id)
        if "error" in chapter_list:
            return chapter_list
        
        # Combine the information
        return {
            "novel_details": novel_details,
            "chapter_list": chapter_list,
            "total_chapters": len(chapter_list.get("data", []))
        }
    
    def download_novel(self, config: FanqieConfig) -> Dict:
        """
        Download a novel using the provided configuration
        
        Args:
            config: FanqieConfig object with download parameters
            
        Returns:
            Dictionary with download results
        """
        if not config.novel_id:
            return {"success": False, "error": "Novel ID is required"}
        
        logger.info("Starting download for novel ID: %s", config.novel_id)
        
        try:
            # Get novel information
            novel_info = self.get_novel_info(config.novel_id)
            if "error" in novel_info:
                return {"success": False, "error": novel_info["error"]}
            
            # Get chapter list
            chapters = novel_info["chapter_list"].get("data", [])
            if not chapters:
                return {"success": False, "error": "No chapters found"}
            
            # Filter chapters by range if specified
            if config.start_chapter or config.end_chapter:
                start = (config.start_chapter or 1) - 1
                end = config.end_chapter or len(chapters)
                chapters = chapters[start:end]
            
            # Download chapters
            downloaded_chapters = []
            output_dir = Path(config.output_path or self.default_output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create novel directory
            novel_details = novel_info["novel_details"].get("data", {})
            novel_title = novel_details.get("title", f"novel_{config.novel_id}")
            novel_dir = output_dir / self._sanitize_filename(novel_title)
            novel_dir.mkdir(parents=True, exist_ok=True)
            
            for i, chapter in enumerate(chapters):
                chapter_id = chapter.get("item_id")
                chapter_title = chapter.get("title", f"Chapter {i+1}")
                
                logger.info("Downloading chapter: %s", chapter_title)
                
                # Get chapter content
                content_response = self.api.get_chapter_content(chapter_id)
                if "error" in content_response:
                    logger.warning("Failed to download chapter %s: %s", chapter_title, content_response["error"])
                    continue
                
                content_data = content_response.get("data", {})
                content = self._format_chapter_content(content_data)
                if not content:
                    content = content_data.get("content", "")
                
                # Save chapter
                if config.format_type == OutputFormat.TXT:
                    chapter_file = novel_dir / f"{i+1:03d}_{self._sanitize_filename(chapter_title)}.txt"
                    with open(chapter_file, 'w', encoding='utf-8') as f:
                        f.write(f"# {chapter_title}\n\n{content}\n")
                    downloaded_chapters.append(str(chapter_file))
                
                # Add delay to respect rate limiting
                import time
                time.sleep(config.request_rate_limit)
            
            return {
                "success": True,
                "novel_title": novel_title,
                "output_path": str(novel_dir),
                "downloaded_chapters": len(downloaded_chapters),
                "chapter_files": downloaded_chapters
            }
            
        except Exception as e:
            logger.error("Download failed: %s", e)
            return {"success": False, "error": str(e)}

    @staticmethod
    def _format_chapter_content(content_data: Dict[str, Any]) -> str:
        """Normalize chapter content to preserve paragraph structure."""

        def _iter_candidates(data: Dict[str, Any]) -> List[str]:
            keys = (
                "content_paragraph",
                "contentParagraph",
                "content_paragraphs",
                "paragraphs",
                "content_list",
                "contentList",
            )
            candidates: List[str] = []
            for key in keys:
                value = data.get(key)
                if isinstance(value, list):
                    candidates.extend(str(item) for item in value if item)
            content_value = data.get("content")
            if isinstance(content_value, list):
                candidates.extend(str(item) for item in content_value if item)
            elif isinstance(content_value, str):
                candidates.append(content_value)
            return candidates

        def _strip_html(raw: str) -> str:
            if not raw:
                return ""
            text = unescape(raw)
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
            text = re.sub(r"</p\s*>", "\n\n", text, flags=re.IGNORECASE)
            text = re.sub(r"<(div|section)[^>]*>", "\n\n", text, flags=re.IGNORECASE)
            text = re.sub(r"<[^>]+>", "", text)
            text = text.replace("&nbsp;", " ")
            return text

        def _is_ascii_alnum(char: str) -> bool:
            return bool(char and char.isascii() and char.isalnum())

        def _join_wrapped_lines(lines: List[str]) -> str:
            if not lines:
                return ""
            text = lines[0]
            for line in lines[1:]:
                if not line:
                    continue
                if not text:
                    text = line
                    continue
                last_char = text[-1]
                first_char = line[0]
                if (
                    _is_ascii_alnum(last_char) and _is_ascii_alnum(first_char)
                ) or (
                    last_char in {'.', '?', '!', ':', ';'} and _is_ascii_alnum(first_char)
                ):
                    text += " " + line
                else:
                    text += line
            return text.strip()

        def _to_paragraphs(cleaned_text: str) -> List[str]:
            if not cleaned_text:
                return []
            lines = [line.strip() for line in cleaned_text.split("\n")]
            paragraphs: List[str] = []
            pending: List[str] = []
            for line in lines:
                if not line:
                    if pending:
                        paragraph = _join_wrapped_lines(pending)
                        if paragraph:
                            paragraphs.append(paragraph)
                        pending = []
                    continue
                pending.append(line)
            if pending:
                paragraph = _join_wrapped_lines(pending)
                if paragraph:
                    paragraphs.append(paragraph)
            return paragraphs

        candidates = _iter_candidates(content_data)
        paragraphs: List[str] = []
        for candidate in candidates:
            cleaned = _strip_html(candidate)
            paragraphs.extend(_to_paragraphs(cleaned))

        if not paragraphs:
            fallback = _strip_html(str(content_data.get("content", "")))
            paragraphs = _to_paragraphs(fallback)

        return "\n\n".join(paragraphs).strip()
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for cross-platform compatibility
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        import re
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = sanitized.strip('. ')
        return sanitized[:100]  # Limit length
    
    def extract_novel_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract novel ID from Fanqie novel URL
        
        Args:
            url: Fanqie novel URL
            
        Returns:
            Novel ID if found, None otherwise
        """
        import re
        # Pattern for Fanqie novel URLs
        pattern = r'fanqienovel\.com/page/(\d+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
    
    def list_downloaded_novels(self, output_dir: Optional[str] = None) -> List[str]:
        """
        Get list of downloaded novels in the output directory
        
        Args:
            output_dir: Directory to check (uses default if None)
            
        Returns:
            List of novel directory names
        """
        # Resolve to a Path so relative vs absolute differences are normalized
        target_dir = Path(output_dir) if output_dir else Path(self.default_output_dir)

        try:
            if target_dir.exists():
                return [
                    item for item in os.listdir(target_dir)
                    if (target_dir / item).is_dir()
                ]
            else:
                return []
        except Exception as e:
            logger.error("Error listing downloaded novels: %s", e)
            return []


# Convenience functions for common use cases

def search_fanqie_novels(query: str) -> Dict:
    """
    Quick function to search for novels
    
    Args:
        query: Search query
        
    Returns:
        Search results dictionary
    """
    downloader = FanqieNovelDownloader()
    return downloader.search_novels(query)


def download_fanqie_novel(
    novel_id: str,
    output_dir: Optional[str] = None,
    format_type: OutputFormat = OutputFormat.TXT,
    chapter_range: Optional[tuple] = None
) -> Dict:
    """
    Quick function to download a novel
    
    Args:
        novel_id: Fanqie novel ID
        output_dir: Output directory
        format_type: Output format (TXT or EPUB)
        chapter_range: Tuple of (start, end) chapter numbers
        
    Returns:
        Download results dictionary
    """
    # Resolve output_dir to repo-root data/raw when not provided
    if output_dir is None:
        repo_root = Path(__file__).resolve().parents[2]
        output_dir = str(repo_root / "data" / "raw")

    downloader = FanqieNovelDownloader(output_dir)

    config = FanqieConfig(
        novel_id=novel_id,
        output_path=output_dir,
        format_type=format_type,
        start_chapter=chapter_range[0] if chapter_range else None,
        end_chapter=chapter_range[1] if chapter_range else None
    )

    return downloader.download_novel(config)


def download_from_fanqie_url(
    url: str,
    output_dir: Optional[str] = None,
    chapter_range: Optional[tuple] = None
) -> Dict:
    """
    Download novel from Fanqie URL
    
    Args:
        url: Fanqie novel URL
        output_dir: Output directory
        chapter_range: Tuple of (start, end) chapter numbers
        
    Returns:
        Download results dictionary
    """
    if output_dir is None:
        repo_root = Path(__file__).resolve().parents[2]
        output_dir = str(repo_root / "data" / "raw")

    downloader = FanqieNovelDownloader(output_dir)
    
    novel_id = downloader.extract_novel_id_from_url(url)
    if not novel_id:
        return {"success": False, "error": "Could not extract novel ID from URL"}
    
    return download_fanqie_novel(novel_id, output_dir, OutputFormat.TXT, chapter_range)