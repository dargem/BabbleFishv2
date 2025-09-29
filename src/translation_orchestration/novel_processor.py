from typing import List, Dict, Optional, Callable, Any
from src.core import Novel, Requirement
from src.workflows.states import SetupState, IngestionState, TranslationState
from src.workflows import (
    SetupWorkflowFactory,
    IngestionWorkflowFactory,
    TranslationWorkflowFactory,
)


class NovelTranslator:
    """Simple orchestrator: get requirement -> fulfill -> update -> repeat until done"""

    def __init__(
        self,
        setup_workflow_factory: SetupWorkflowFactory,
        ingestion_workflow_factory: IngestionWorkflowFactory,
        translation_workflow_factory: TranslationWorkflowFactory,
        novel: Optional[Novel] = None,
    ):
        """
        Constructor with proper dependency injection

        Args:
            setup_workflow_factory: Factory for creating setup workflows
            ingestion_workflow_factory: Factory for creating ingestion workflows
            translation_workflow_factory: Factory for creating translation workflows
            novel: Optional preloaded novel object to continue translation on
        """
        self.setup_workflow_factory = setup_workflow_factory
        self.ingestion_workflow_factory = ingestion_workflow_factory
        self.translation_workflow_factory = translation_workflow_factory
        self.novel = novel if novel else Novel()

    def add_chapters(self, indexed_chapters: Dict[int, str]):
        """
        Adds extra chapters to the novel object

        Args:
            indexed_chapters: strings of chapters indexed by integer
        """
        self.novel.add_chapters(indexed_chapters)

    def get_next_requirement(self) -> Optional[tuple]:
        """
        Gets the next requirement from the novel that needs to be fulfilled

        Returns:
            Tuple of (chapter_index, chapter_text, requirement) or None if no requirements left
        """
        return self.novel.get_task()

    async def fulfill_requirement(self, requirement: tuple) -> Dict[str, any]:
        """
        Fulfills a single requirement and updates the novel accordingly

        Args:
            requirement: Tuple of (chapter_index, chapter_text, requirement_type)

        Returns:
            Dictionary containing the fulfillment result
        """
        chapter_index, chapter_text, requirement_type = requirement

        # Handle novel-level requirements
        if chapter_index == -1:
            return await self._fulfill_novel_requirement(chapter_text, requirement_type)

        # Handle chapter-level requirements
        return await self._fulfill_chapter_requirement(
            chapter_index, chapter_text, requirement_type
        )

    async def _fulfill_novel_requirement(
        self, sample_text: str, requirement_type: Requirement
    ) -> Dict[str, any]:
        """Fulfill a novel-level requirement (style guide, genres, language)"""
        setup_workflow = self.setup_workflow_factory.create_workflow([requirement_type])
        setup_state = SetupState(text=sample_text)

        result = await setup_workflow.ainvoke(setup_state)

        # Update novel with result
        if "style_guide" in result and result["style_guide"]:
            self.novel.style_guide = result["style_guide"].strip()
        if "genres" in result and result["genres"]:
            self.novel.genres = result["genres"]
        if "language" in result and result["language"]:
            self.novel.language = result["language"].strip()

        return result

    async def _fulfill_chapter_requirement(
        self, chapter_index: int, chapter_text: str, requirement_type: Requirement
    ) -> Dict[str, any]:
        """Fulfill a chapter-level requirement (ingestion, translation, etc.)"""
        chapter = self.novel.indexed_chapters[chapter_index]

        match requirement_type:
            case Requirement.SUMMARY:
                chapter.summary = "Generated summary placeholder"
                return {"summary": chapter.summary}

            case Requirement.INGESTION:
                ingestion_workflow = self.ingestion_workflow_factory.create_workflow()
                ingestion_state = IngestionState(
                    text=chapter_text, entities=[], new_entities=[], triplets=[]
                )
                result = await ingestion_workflow.ainvoke(ingestion_state)
                chapter.ingested_status = True
                return result

            case Requirement.ANNOTATION:
                chapter.annotated_status = True
                return {"annotation": "completed"}

            case Requirement.TRANSLATION:
                translation_workflow = (
                    self.translation_workflow_factory.create_workflow()
                )
                translation_state = TranslationState(
                    text=chapter_text,
                    style_guide=self.novel.style_guide or "",
                    language=self.novel.language or "",
                    translation="",
                    fluent_translation="",
                    feedback="",
                    feedback_rout_loops=0,
                )
                result = await translation_workflow.ainvoke(translation_state)
                chapter.translation = result.get(
                    "fluent_translation", result.get("translation", "")
                )
                return result

            case _:
                raise NotImplementedError(
                    f"Requirement type {requirement_type.value} not implemented"
                )

    def print_status(self):
        """Print current novel processing status"""
        total_chapters = len(self.novel.indexed_chapters)
        ingested = sum(
            1 for ch in self.novel.indexed_chapters.values() if ch.ingested_status
        )
        translated = sum(
            1
            for ch in self.novel.indexed_chapters.values()
            if ch.translation is not None
        )

        print(f"\nFINAL STATUS:")
        print(f"Setup complete: {len(self.novel.get_novel_requirements()) == 0}")
        print(f"Style guide: {'Complete' if self.novel.style_guide else 'Failed'}")
        print(f"Genres: {self.novel.genres if self.novel.genres else 'Failed'}")
        print(f"Language: {self.novel.language if self.novel.language else 'Failed'}")
        print(f"Chapters ingested: {ingested}/{total_chapters}")
        print(f"Chapters translated: {translated}/{total_chapters}")
