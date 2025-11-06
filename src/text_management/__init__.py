"""Manages loading texts into Novel objects"""

from .lightnovel_crawler import (
    FanqieNovelDownloader,
    FanqieAPI,
    FanqieConfig,
    OutputFormat,
    search_fanqie_novels,
    download_fanqie_novel,
    download_from_fanqie_url,
)

from .novel_loader import (
    NovelLoader
)

__all__ = [
    # Low-level Fanqie API interface
    "FanqieNovelDownloader",
    "FanqieAPI",
    "FanqieConfig",
    "OutputFormat",
    "search_fanqie_novels",
    "download_fanqie_novel",
    "download_from_fanqie_url",
    "NovelLoader"
]
