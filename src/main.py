"""Entry point for translator"""

# type hints
from __future__ import annotations

# imports
import asyncio
import logging
from pathlib import Path
from src.config import ConfigFactory, Container

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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
        logger.error("Test file not found at %s", file_path)
        return

    with open(file_path, "r", encoding="UTF-8") as f:
        chapter_text = f.read()

    # Add chapter to novel
    novel_processor.add_chapters({1: chapter_text})

    logger.info("Starting Translation Process")

    # get requirement -> fulfill -> update -> repeat
    task_count = 0
    while True:
        # Get next requirement from novel
        requirement = novel_processor.get_next_requirement()
        if not requirement:
            logger.info("All requirements completed")
            break

        task_count += 1
        chapter_index, chapter_text, requirement_type = requirement

        logger.info("Task %d: %s", task_count, requirement_type.value)
        if chapter_index == -1:
            logger.debug("Processing novel-level requirement")
        else:
            logger.debug("Processing chapter %d requirement", chapter_index)

        # Fulfill the requirement
        try:
            result = await novel_processor.fulfill_requirement(requirement)
            logger.info("Completed: %s", requirement_type.value)
        except Exception as e:
            logger.error(
                "Failed to process requirement %s: %s", requirement_type.value, e
            )
            break

    logger.info("Processed %d requirements total", task_count)
    novel_processor.print_status()


if __name__ == "__main__":
    asyncio.run(run_complete_translation())
