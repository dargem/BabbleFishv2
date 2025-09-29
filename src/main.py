"""Entry point for translator"""

# type hints
from __future__ import annotations

# imports
import asyncio
from pathlib import Path
from src.config import ConfigFactory, Container
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # go up from src/ to project root
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "lotm_files"


async def run_complete_translation():
    """Simple loop: get requirement -> fulfill -> update -> repeat until done."""

    # Initialize container
    config = ConfigFactory.create_config(env="development")
    container = Container()
    await container.set_config(config)

    novel_processor = container.get_novel_translator()

    # Load a chapter
    file_path = DATA_DIR / "lotm1.txt"
    if not file_path.exists():
        print("No test file found")
        return

    with open(file_path, "r", encoding="UTF-8") as f:
        chapter_text = f.read()

    # Add chapter to novel
    novel_processor.add_chapters({1: chapter_text})

    print("=" * 30)
    print("Starting Translation")
    print("=" * 30)

    # get requirement -> fulfill -> update -> repeat
    task_count = 0
    while True:
        # Get next requirement from novel
        requirement = novel_processor.get_next_requirement()
        if not requirement:
            print("All requirements completed")
            break

        task_count += 1
        chapter_index, chapter_text, requirement_type = requirement

        print(f"\nTask {task_count}: {requirement_type.value}")
        if chapter_index == -1:
            print("Novel-level requirement")
        else:
            print(f"Chapter {chapter_index} requirement")

        # Fulfill the requirement
        try:
            result = await novel_processor.fulfill_requirement(requirement)
            print(f"Completed: {requirement_type.value}")
        except Exception as e:
            print(f"Failed: {e}")
            break

    print(f"\nProcessed {task_count} requirements total")
    novel_processor.print_status()


if __name__ == "__main__":
    asyncio.run(run_complete_translation())
