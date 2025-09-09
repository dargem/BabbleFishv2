"""Main application module for BabbleFish Translation System."""

import sys
from pathlib import Path

# Add the parent directory to sys.path to enable relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflow import create_translation_workflow
from src.workflow import create_ingestion_workflow
from knowledge_graph import KnowledgeGraphManager


def run_translation():
    """Main function to run the translation workflow."""
    kg = KnowledgeGraphManager()
    kg.reset_database()

    with open("../data/raw/lotm_files/lotm2.txt", "r", encoding="UTF-8") as f:
        sample_text = f.read()
    print("Loaded text from file")

    # Database Ingestion
    print("Ingesting new entries...")
    state_input = {"knowledge_graph": kg, "text": sample_text}
    # Create workflow
    ingestion_app = create_ingestion_workflow()
    # run it
    result = ingestion_app.invoke(state_input)
    print("Ingested entries")
    for entity in result["entities"]:
        print(entity)

    exit()
    # Create workflow
    print("Creating translation workflow...")
    translation_app = create_translation_workflow()
    # run workflow
    print("Starting translation process...")
    state_input = {"text": sample_text}
    result = translation_app.invoke(state_input)

    # Print results
    print("\n" + "=" * 50)
    print("TRANSLATION RESULTS")
    print("=" * 50)

    for key in result:
        if isinstance(result[key], str) and result[key].strip():
            print(f"\n{key.upper()}:")
            print("-" * len(key))
            print(result[key])

    # Generate workflow visualization
    try:
        mermaid_code = translation_app.get_graph().draw_mermaid()
        md_content = (
            f"""# Translation Workflow Graph\n\n```mermaid\n{mermaid_code}\n```\n"""
        )
        with open("../workflow_graph.md", "w") as f:
            f.write(md_content)
        print("\nWorkflow diagram saved to workflow_graph.md")
    except Exception as e:
        print(f"Error generating workflow diagram: {e}")


if __name__ == "__main__":
    run_translation()
