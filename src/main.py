"""Main application module for BabbleFish Translation System."""

# type hints
from __future__ import annotations

# imports
import asyncio
from pathlib import Path
from src.config import ConfigFactory, Container

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # go up from src/ to project root
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "lotm_files"


async def run_translation():
    """Main function to run the translation workflow."""

    config = ConfigFactory.create_config(env="development")
    container = Container()
    await container.set_config(config)
    ingestion_app = container.get_ingestion_workflow()
    translation_app = container.get_translation_workflow()

    # Use absolute path based on script location
    script_dir = Path(__file__).parent.parents
    file_path = DATA_DIR / "lotm3.txt"

    with open(file_path, "r", encoding="UTF-8") as f:
        sample_text = f.read()
    print("Loaded text from file")

    kg = container._get_knowledge_graph_manager()
    kg.reset_database()
    print(kg.get_stats())

    # Database Ingestion
    state_input = {"text": sample_text}
    result = await ingestion_app.ainvoke(state_input)

    print("Ingested entries")
    print(kg.get_stats())
    for entity in result["entities"]:
        print(entity.strong_names)

    for triplet in result["triplets"]:
        if triplet.metadata.importance >= 0:
            print(
                f"Name: {triplet.subject_name}, Predicate: {triplet.predicate}, Object: {triplet.object_name}"
            )
            # print(triplet.metadata.__dict__)
    print(kg.get_stats())
    print(kg.get_all_entities())
    print(kg.get_entity_relationships())
    exit()
    # Create workflow
    print("Creating translation workflow...")
    # run workflow
    print("Starting translation process...")
    state_input = {"text": sample_text}
    result = await translation_app.ainvoke(state_input)

    # Print results
    print("\n" + "=" * 50)
    print("TRANSLATION RESULTS")
    print("=" * 50)

    for key in result:
        if isinstance(result[key], str) and result[key].strip():
            print(f"\n{key.upper()}:")
            print("-" * len(key))
            # print(result[key])

    # Generate workflow visualization
    try:
        mermaid_code = translation_app.get_graph().draw_mermaid()
        md_content = (
            f"""# Translation Workflow Graph\n\n```mermaid\n{mermaid_code}\n```\n"""
        )
        output_path = script_dir / "workflow_graph.md"
        with open(output_path, "w") as f:
            f.write(md_content)
        print(f"\nWorkflow diagram saved to {output_path}")
    except Exception as e:
        print(f"Error generating workflow diagram: {e}")


if __name__ == "__main__":
    asyncio.run(run_translation())
