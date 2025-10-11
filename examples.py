"""
Examples demonstrating the Fanqie novel downloader functionality.

This module shows how to use the new Fanqie-novel-Downloader integration
to search for, download, and process Chinese novels from the 番茄小说 platform.
"""

import asyncio
from pathlib import Path
from src.text_management import (
    FanqieNovelDownloader, 
    FanqieConfig,
    FanqieAPI,
    OutputFormat,
    NovelTextLoader,
    search_fanqie_novels,
    download_fanqie_novel,
    load_novel_from_fanqie_url,
    search_and_load_fanqie_novel
)
from src.core.novels import Novel


def example_search_novels():
    """Example: Search for novels by keyword."""
    print("=== Example: Search for novels ===")
    
    try:
        # Use the convenience function
        results = search_fanqie_novels("修仙")
        
        if results.get("success"):
            novels = results.get("data", [])
            print(f"Found {len(novels)} novels:")
            
            for i, novel in enumerate(novels[:5], 1):  # Show first 5 results
                print(f"{i}. {novel.get('title', 'Unknown Title')}")
                print(f"   Author: {novel.get('author', 'Unknown Author')}")
                print(f"   ID: {novel.get('novel_id', 'Unknown ID')}")
                description = novel.get('description', 'No description')
                print(f"   Description: {description[:100]}...")
                print()
        else:
            print(f"Search failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Search failed: {e}")


def example_get_novel_details():
    """Example: Get detailed information about a specific novel."""
    print("=== Example: Get novel details ===")
    
    downloader = FanqieNovelDownloader()
    
    # Example novel ID (you'll need to replace with a real one)
    novel_id = "7143038691944959011"
    
    try:
        details = downloader.get_novel_info(novel_id)
        
        if details.get("success"):
            novel_data = details.get("data", {})
            print(f"Title: {novel_data.get('title', 'Unknown')}")
            print(f"Author: {novel_data.get('author', 'Unknown')}")
            print(f"Status: {novel_data.get('status', 'Unknown')}")
            print(f"Word Count: {novel_data.get('word_count', 'Unknown')}")
            print(f"Description: {novel_data.get('description', 'No description')}")
            print()
        else:
            print(f"Failed to get details: {details.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Failed to get novel details: {e}")


def example_direct_api():
    """Example: Using the direct API interface."""
    print("=== Example: Direct API ===")
    
    api = FanqieAPI()
    
    try:
        # Search using direct API
        search_results = api.search_novels("都市")
        print(f"Direct API search results: {search_results}")
        
        # Get novel details using direct API (replace with real ID)
        novel_id = "7143038691944959011"
        details = api.get_novel_details(novel_id)
        print(f"Novel details: {details}")
        
    except Exception as e:
        print(f"Direct API failed: {e}")


def example_download_novel():
    """Example: Download a novel."""
    print("=== Example: Download novel ===")
    
    # Example novel ID (you'll need to replace with a real one)
    novel_id = "7143038691944959011"
    
    try:
        # Download using convenience function
        result = download_fanqie_novel(
            novel_id=novel_id,
            output_dir="./data/raw",
            format_type=OutputFormat.TXT,
            chapter_range=(1, 3)  # Download only first 3 chapters for testing
        )
        
        if result.get("success"):
            print(f"Novel downloaded successfully!")
            print(f"Output: {result.get('output_path', 'Unknown path')}")
        else:
            print(f"Download failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Download failed: {e}")


def example_novel_object_integration():
    """Example: Using NovelTextLoader to integrate with Novel objects."""
    print("=== Example: Novel object integration ===")
    
    # Example: Load from Fanqie URL using convenience function
    fanqie_url = "https://fanqienovel.com/page/7143038691944959011"
    
    try:
        novel = load_novel_from_fanqie_url(fanqie_url, chapter_limit=2)
        
        if novel:
            print(f"Novel loaded successfully!")
            print(f"Number of chapters: {len(novel.indexed_chapters)}")
            print(f"Language: {novel.language}")
            
            # Get content from all chapters
            all_text = novel.all_chapter_text
            if all_text:
                full_content = " ".join(all_text)
                print(f"Total content length: {len(full_content)} characters")
                print(f"Content preview: {full_content[:200]}...")
            else:
                print("No content found")
        else:
            print("Failed to load novel")
        
    except Exception as e:
        print(f"Failed to load novel: {e}")


def example_search_and_load():
    """Example: Search for a novel and load the first result."""
    print("=== Example: Search and load ===")
    
    try:
        # Search for novels about "都市" (urban/modern) and load the first result
        novel = search_and_load_fanqie_novel("都市", chapter_limit=2)
        
        if novel:
            print(f"Novel loaded successfully!")
            print(f"Number of chapters: {len(novel.indexed_chapters)}")
            
            # Get content from all chapters
            all_text = novel.all_chapter_text
            if all_text:
                full_content = " ".join(all_text)
                print(f"Total content length: {len(full_content)} characters")
                print(f"Content preview: {full_content[:200]}...")
            else:
                print("No content found")
        else:
            print("No novels found or failed to load")
            
    except Exception as e:
        print(f"Search and load failed: {e}")


def example_url_extraction():
    """Example: Extract novel ID from Fanqie URLs."""
    print("=== Example: URL extraction ===")
    
    downloader = FanqieNovelDownloader()
    
    # Example URLs
    urls = [
        "https://fanqienovel.com/page/7143038691944959011",
        "https://fanqienovel.com/page/7143038691944959011?cid=7143038758174687267",
        "https://m.fanqienovel.com/page/7143038691944959011",
        "invalid_url"
    ]
    
    for url in urls:
        novel_id = downloader.extract_novel_id_from_url(url)
        print(f"URL: {url}")
        print(f"Extracted ID: {novel_id}")
        print()


def main():
    """Run all examples."""
    print("Fanqie Novel Downloader Examples")
    print("=" * 40)
    print()
    
    # Run all examples
    example_url_extraction()
    example_search_novels()
    example_get_novel_details()
    example_direct_api()
    example_download_novel()
    example_novel_object_integration()
    example_search_and_load()
    
    print("=" * 40)
    print("All examples completed!")


if __name__ == "__main__":
    # Note: You'll need to replace the example novel IDs and URLs with real ones
    # from the Fanqie platform for these examples to work.
    
    print("Note: Replace example novel IDs with real ones from fanqienovel.com")
    print("for these examples to work properly.")
    print()
    
    main()