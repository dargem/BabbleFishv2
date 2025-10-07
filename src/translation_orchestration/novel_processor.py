import logging
from typing import Dict, Optional, Any
from src.core import Novel, Requirement
from src.translation_orchestration.workflow_registry import (
    WorkflowRegistry,
    RequirementExecutionContext,
)

logger = logging.getLogger(__name__)


class NovelTranslator:
    """Simplified orchestrator using workflow registry: get requirement -> fulfill -> update -> repeat until done"""

    def __init__(
        self,
        workflow_registry: WorkflowRegistry,
        novel: Optional[Novel] = None,
    ):
        """
        Constructor with workflow registry dependency injection

        Args:
            workflow_registry: Registry for managing and executing workflows
            novel: Optional preloaded novel object to continue translation on
        """
        self.workflow_registry = workflow_registry
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
        Fulfills a single requirement using the workflow registry

        Args:
            requirement: Tuple of (chapter_index, chapter_text, requirement_type)

        Returns:
            Dictionary containing the fulfillment result
        """
        chapter_index, chapter_text, requirement_type = requirement

        # Create execution context with novel context for chapter-level requirements
        novel_context = {
            "style_guide": self.novel.style_guide,
            "genres": self.novel.genres,
            "language": self.novel.language,
        }

        context = RequirementExecutionContext(
            chapter_index=chapter_index,
            chapter_text=chapter_text,
            requirement_type=requirement_type,
            novel_context=novel_context,
        )

        # Execute using workflow registry
        result = await self.workflow_registry.execute_requirement(context)

        # Update novel state based on requirement type and result
        await self._update_novel_state(chapter_index, requirement_type, result)

        return result

    async def _update_novel_state(
        self, chapter_index: int, requirement_type: Requirement, result: Dict[str, Any]
    ) -> None:
        """
        Update the novel state based on the requirement execution result

        Args:
            chapter_index: Index of the chapter (-1 for novel-level)
            requirement_type: Type of requirement that was fulfilled
            result: Result from requirement execution
        """
        # Handle novel-level requirements
        if chapter_index == -1:
            self.novel.style_guide = (
                result["style_guide"].strip() if result["style_guide"] else None
            )
            logger.info(self.novel.style_guide)
            self.novel.genres = result["genres"]
            logger.info(self.novel.genres)
            self.novel.language = (
                result["language"].strip() if result["language"] else None
            )
            logger.info(self.novel.language)
            return

        # Handle chapter-level requirements
        chapter = self.novel.indexed_chapters[chapter_index]

        match requirement_type:
            case Requirement.SUMMARY:
                chapter.summary = result.get("summary")
            case Requirement.INGESTION:
                chapter.ingested_status = True
            case Requirement.ANNOTATION:
                chapter.annotated_status = True
            case Requirement.TRANSLATION:
                chapter.translation = result.get(
                    "fluent_translation", result.get("translation", "")
                )
            case _:
                pass  # Unknown requirement type, no state update needed

    def print_status(self):
        """Log current novel processing status"""
        total_chapters = len(self.novel.indexed_chapters)
        ingested = sum(
            1 for ch in self.novel.indexed_chapters.values() if ch.ingested_status
        )
        translated = sum(
            1
            for ch in self.novel.indexed_chapters.values()
            if ch.translation is not None
        )

        logger.info("FINAL STATUS:")
        logger.info(
            "Setup complete: %s", False if self.novel.get_novel_requirements() else True
        )
        logger.info(
            "Style guide: %s", "Complete" if self.novel.style_guide else "Failed"
        )
        logger.info("Genres: %s", self.novel.genres if self.novel.genres else "Failed")
        logger.info(
            "Language: %s", self.novel.language if self.novel.language else "Failed"
        )
        logger.info("Chapters ingested: %d/%d", ingested, total_chapters)
        logger.info("Chapters translated: %d/%d", translated, total_chapters)
