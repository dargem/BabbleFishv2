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
    NovelTextLoader,
    load_novel_from_fanqie_url,
    load_novel_from_fanqie_id,
    search_and_load_fanqie_novel,
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
    # High-level novel loading interface
    "NovelTextLoader",
    "load_novel_from_fanqie_url",
    "load_novel_from_fanqie_id",
    "search_and_load_fanqie_novel",
]
