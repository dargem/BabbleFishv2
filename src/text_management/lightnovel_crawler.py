"""Minimal Fanqie API interface for novel downloading."""

import logging
import requests
from typing import Dict, Optional, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from html import unescape
import re

logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Supported output formats"""

    TXT = "1"


@dataclass
class FanqieConfig:
    """Configuration for downloading"""

    novel_id: Optional[str] = None
    output_path: Optional[str] = None
    format_type: OutputFormat = OutputFormat.TXT
    start_chapter: Optional[int] = None
    end_chapter: Optional[int] = None
    max_workers: int = 4
    max_retries: int = 3
    request_timeout: int = 15
    request_rate_limit: float = 0.4
    download_enabled: bool = True


class FanqieAPI:
    """API interface for Fanqie novels - chapter content and directory"""

    BASE_URL = "https://fanqienovel.com/api/reader"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def get_chapter_list(self, novel_id: str) -> Dict:
        """Get chapter list for a novel"""
        try:
            url = f"{self.BASE_URL}/directory/detail"
            response = self.session.get(
                url, params={"bookId": novel_id}, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                # chapterListWithVolume is a list of volumes, each containing chapters
                volumes = data["data"].get("chapterListWithVolume", [])
                # Flatten all chapters from all volumes into a single list
                all_chapters = []
                for volume in volumes:
                    if isinstance(volume, list):
                        all_chapters.extend(volume)
                return {"chapters": all_chapters}
            return {"chapters": []}
        except Exception as e:
            logger.error("Failed to get chapter list: %s", e)
            return {"chapters": []}

    def get_chapter_content(self, chapter_id: str, book_id: str) -> Dict:
        """Get content for a specific chapter"""
        try:
            url = f"{self.BASE_URL}/chapter"
            response = self.session.get(
                url,
                params={"chapterId": chapter_id, "bookId": book_id},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get chapter content: %s", e)
            return {"error": str(e)}


class TomatoAPI:
    """Tomato API for book details (title, author, description)"""

    BASE_URL = "http://43.248.77.205:55555"
    ENDPOINTS = {
        "detail": "/api/detail",
        "directory": "/api/directory",
        "content": "/api/content",
    }

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def get_book_detail(self, book_id: str) -> Optional[Dict]:
        """Get book details (title, author, description, cover)"""
        try:
            url = self.BASE_URL + self.ENDPOINTS["detail"]
            response = self.session.get(
                url, params={"book_id": book_id}, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            raw = data.get("data", data)
            if isinstance(raw, dict) and "data" in raw and len(raw) <= 3:
                raw = raw.get("data")

            if isinstance(raw, dict) and raw.get("code") in [101109, 101110]:
                return None

            if isinstance(raw, dict):
                return {
                    "book_id": str(raw.get("book_id") or book_id),
                    "book_name": raw.get("book_name") or raw.get("title") or "Unknown",
                    "author": raw.get("author")
                    or raw.get("author_name")
                    or "Unknown Author",
                    "intro": raw.get("intro") or raw.get("abstract") or "",
                    "cover": raw.get("cover") or raw.get("cover_url") or "",
                }
            return None
        except Exception as e:
            logger.error("Failed to get book detail: %s", e)
            return None


class FanqieNovelDownloader:
    """Main downloader interface"""

    def __init__(self, default_output_dir: Optional[str] = None):
        """Initialize the downloader"""
        repo_root = Path(__file__).resolve().parents[2]
        default_data_dir = repo_root / "data" / "raw"
        self.default_output_dir = str(
            Path(default_output_dir) if default_output_dir else default_data_dir
        )
        self.fanqie_api = FanqieAPI()
        self.tomato_api = TomatoAPI()
        self._verify_installation()

    def _verify_installation(self) -> bool:
        """Check if APIs are accessible"""
        try:
            url = f"{self.fanqie_api.BASE_URL}/directory/detail"
            response = requests.get(url, params={"bookId": "1"}, timeout=5)
            if response.status_code == 200:
                logger.info("Fanqie API accessible")
                return True
        except Exception as e:
            logger.warning("Fanqie API test failed: %s", e)

        return False

    def get_novel_info(self, novel_id: str) -> Dict:
        """Get novel details and chapter list"""
        book_detail = self.tomato_api.get_book_detail(novel_id) or {
            "book_id": novel_id,
            "book_name": f"Novel {novel_id}",
            "author": "Unknown",
            "intro": "",
            "cover": "",
        }

        chapter_list = self.fanqie_api.get_chapter_list(novel_id)

        return {
            "book_detail": book_detail,
            "chapter_list": chapter_list,
            "total_chapters": len(chapter_list.get("chapters", [])),
        }

    def download_novel(self, config: FanqieConfig) -> Dict:
        """Download a novel"""
        if not config.novel_id:
            return {"success": False, "error": "Novel ID is required"}

        try:
            novel_info = self.get_novel_info(config.novel_id)
            chapters = novel_info["chapter_list"].get("chapters", [])

            if not chapters:
                return {"success": False, "error": "No chapters found"}

            # Filter chapters by range
            if config.start_chapter or config.end_chapter:
                start = (config.start_chapter or 1) - 1
                end = config.end_chapter or len(chapters)
                chapters = chapters[start:end]

            downloaded_chapters = []
            output_dir = Path(config.output_path or self.default_output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            book_detail = novel_info.get("book_detail", {})
            novel_title = book_detail.get("book_name", f"novel_{config.novel_id}")
            novel_dir = output_dir / self._sanitize_filename(novel_title)
            novel_dir.mkdir(parents=True, exist_ok=True)

            for i, chapter in enumerate(chapters):
                # Handle both camelCase (itemId) and snake_case (item_id)
                chapter_id = chapter.get("itemId") or chapter.get("item_id")
                chapter_title = chapter.get("title", f"Chapter {i + 1}")

                logger.info("Downloading chapter: %s", chapter_title)

                content_response = self.fanqie_api.get_chapter_content(
                    chapter_id, config.novel_id
                )
                if "error" in content_response:
                    logger.warning("Failed to download chapter %s", chapter_title)
                    continue

                content_data = content_response.get("data", {})
                content = self._format_chapter_content(content_data)
                if not content:
                    content = content_data.get("content", "")

                chapter_file = (
                    novel_dir
                    / f"{i + 1:03d}_{self._sanitize_filename(chapter_title)}.txt"
                )
                with open(chapter_file, "w", encoding="utf-8") as f:
                    f.write(f"# {chapter_title}\n\n{content}\n")
                downloaded_chapters.append(str(chapter_file))

                import time

                time.sleep(config.request_rate_limit)

            return {
                "success": True,
                "novel_title": novel_title,
                "output_path": str(novel_dir),
                "downloaded_chapters": len(downloaded_chapters),
                "chapter_files": downloaded_chapters,
            }

        except Exception as e:
            logger.error("Download failed: %s", e)
            return {"success": False, "error": str(e)}

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename for file system"""
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)
        return filename[:200]

    @staticmethod
    def _format_chapter_content(content_data: Dict) -> str:
        """Format chapter content by removing HTML and preserving paragraphs"""
        if isinstance(content_data, str):
            content = content_data
        else:
            content = content_data.get("content", "")

        if not content:
            return ""

        # Remove HTML tags
        content = re.sub(r"<[^>]+>", "", content)
        content = unescape(content)

        # Handle <br/> and similar tags
        content = re.sub(r"&lt;br/?&gt;", "\n", content)

        # Split into lines and rejoin
        lines = [line.rstrip() for line in content.split("\n")]

        # Detect wrapped lines and rejoin them
        cleaned_lines = []
        current_line = ""
        for line in lines:
            if (
                line
                and not line[0].isupper()
                and current_line
                and not current_line.endswith(("。", "！", "？", ".", "!", "?"))
            ):
                current_line += line
            else:
                if current_line:
                    cleaned_lines.append(current_line)
                current_line = line
        if current_line:
            cleaned_lines.append(current_line)

        # Join lines preserving paragraph breaks
        result = "\n\n".join([line for line in cleaned_lines if line.strip()])

        return result.strip()

    def search_novels(self, query: str) -> Dict:
        """Search for novels"""
        return {"error": "Search not implemented"}

    def list_downloaded_novels(self) -> List[str]:
        """List downloaded novels"""
        output_dir = Path(self.default_output_dir)
        if not output_dir.exists():
            return []
        return [d.name for d in output_dir.iterdir() if d.is_dir()]

    def extract_novel_id_from_url(self, url: str) -> Optional[str]:
        """Extract novel ID from Fanqie URL"""
        match = re.search(r"/page/(\d+)", url)
        if match:
            return match.group(1)
        return None


# Convenience functions for backwards compatibility


def search_fanqie_novels(query: str) -> Dict:
    """Search for novels (stub)"""
    return {"error": "Search not implemented"}


def download_fanqie_novel(
    novel_id: str,
    output_dir: Optional[str] = None,
    format_type: OutputFormat = OutputFormat.TXT,
    chapter_range: Optional[tuple] = None,
) -> Dict:
    """Download a novel (stub)"""
    downloader = FanqieNovelDownloader(output_dir)
    config = FanqieConfig(
        novel_id=novel_id, output_path=output_dir, format_type=format_type
    )
    if chapter_range:
        config.start_chapter, config.end_chapter = chapter_range
    return downloader.download_novel(config)


def download_from_fanqie_url(
    url: str,
    output_dir: Optional[str] = None,
    format_type: OutputFormat = OutputFormat.TXT,
    chapter_range: Optional[tuple] = None,
) -> Dict:
    """Download from URL (stub)"""
    downloader = FanqieNovelDownloader(output_dir)
    novel_id = downloader.extract_novel_id_from_url(url)
    if not novel_id:
        return {"success": False, "error": "Could not extract novel ID from URL"}
    return download_fanqie_novel(novel_id, output_dir, format_type, chapter_range)
