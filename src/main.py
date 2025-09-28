"""Main application module for BabbleFish Translation System."""

# type hints
from __future__ import annotations

# imports
import asyncio
from pathlib import Path
from src.config import ConfigFactory, Container
from src.knowledge_graph import KnowledgeGraphManager
from src.translation_orchestration.novel_processor import NovelTranslator
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # go up from src/ to project root
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "lotm_files"


async def run_step_by_step_translation():
    """Example of running step-by-step translation using the task-based approach."""

    # Initialize container
    config = ConfigFactory.create_config(env="development")
    container = Container()
    await container.set_config(config)

    novel_translator = container.get_novel_translator()

    # Load a chapter, should have another class for this later
    file_path = DATA_DIR / "lotm1.txt"
    if not file_path.exists():
        print("No test file found")
        return

    with open(file_path, "r", encoding="UTF-8") as f:
        chapter_text = f.read()

    # Add chapter
    novel_translator.add_chapters({1: chapter_text})

    print("=" * 50)
    print("STEP-BY-STEP TRANSLATION")
    print("=" * 50)

    # Process tasks one by one
    task_count = 0
    while True:
        task = await novel_translator.get_next_task()
        if not task:
            print("\nAll tasks completed!")
            break

        task_count += 1
        chapter_idx, chapter_text, requirement = task

        print(f"\nTask {task_count}: {requirement.value} for chapter {chapter_idx}")

        try:
            result = await novel_translator.process_next_task(sample_text=chapter_text)
            print(f"{requirement.value} completed successfully")

            # Show brief result summary
            if isinstance(result, dict):
                if "style_guide" in result:
                    print(
                        f"  Generated style guide ({len(result['style_guide'])} characters)"
                    )
                if "language" in result:
                    print(f"  Detected language: {result['language']}")
                if "genres" in result:
                    print(f"  Detected genres: {result['genres']}")
                if "entities" in result:
                    print(f"  Extracted {len(result.get('entities', []))} entities")
                if "translation" in result or "fluent_translation" in result:
                    translation = result.get("fluent_translation") or result.get(
                        "translation", ""
                    )
                    print(f"  Translation generated ({len(translation)} characters)")

        except Exception as e:
            print(f"{requirement.value} failed: {e}")

    # Show final status
    status = novel_translator.get_novel_status()
    print(f"\n" + "=" * 40)
    print("FINAL STATUS")
    print("=" * 40)
    print(f"Setup complete: {status['setup_complete']}")
    print(
        f"Chapters ingested: {status['ingested_chapters']}/{status['total_chapters']}"
    )
    print(
        f"Chapters translated: {status['translated_chapters']}/{status['total_chapters']}"
    )


if __name__ == "__main__":
    asyncio.run(run_step_by_step_translation())
