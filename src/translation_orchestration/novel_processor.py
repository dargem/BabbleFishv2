from typing import List, Dict, Optional, Callable, Any
from src.core import Novel, Requirement
from src.workflows.states import SetupState, IngestionState, TranslationState
from src.workflows import (
    SetupWorkflowFactory,
    IngestionWorkflowFactory,
    TranslationWorkflowFactory,
)


class NovelTranslator:
    """Orchestrator for the sequential translation process using setup, ingestion, and translation workflows"""

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

        # Cache for workflow instances
        self._workflow_cache: Dict[str, Any] = {}

    def add_chapters(self, indexed_chapters: Dict[int, str]):
        """
        Adds extra chapters to the novel object

        Args:
            indexed_chapters: strings of chapters indexed by integer
        """
        self.novel.add_chapters(indexed_chapters)

    async def setup_novel(self, text: str) -> Dict[str, any]:
        """
        Runs the setup workflow to analyze the novel's style, genre, and language

        Args:
            text: Sample text to analyze (first chapter or representative excerpt)

        Returns:
            Dictionary containing setup results
        """

        requirements = self.novel.get_novel_requirements()

        if not requirements:
            return {
                "style_guide": self.novel.style_guide,
                "genres": self.novel.genres,
                "language": self.novel.language,
            }

        # Process requirements one at a time to ensure proper state updates
        all_results = {}

        for requirement in requirements:
            print(f"Processing setup requirement: {requirement.value}")
            setup_workflow = self._get_or_create_setup_workflow([requirement])
            setup_state = SetupState(text=text)

            result = await setup_workflow.ainvoke(setup_state)

            # Update novel state immediately for this requirement
            self._update_novel_from_setup_result(result)

            # Merge results
            all_results.update(result)

            print(f"✓ Completed {requirement.value}")

        return all_results

    def _update_novel_from_setup_result(self, result: Dict[str, any]):
        """
        Update novel properties from setup workflow results

        Args:
            result: Dictionary containing setup results
        """
        updated = False

        if (
            "style_guide" in result
            and result["style_guide"]
            and result["style_guide"].strip()
        ):
            self.novel.style_guide = result["style_guide"].strip()
            print(f"Updated style_guide: {len(self.novel.style_guide)} characters")
            updated = True

        if "genres" in result and result["genres"]:
            self.novel.genres = result["genres"]
            print(f"Updated genres: {self.novel.genres}")
            updated = True

        if "language" in result and result["language"] and result["language"].strip():
            self.novel.language = result["language"].strip()
            print(f"Updated language: {self.novel.language}")
            updated = True

        if updated:
            # Verify the requirements are now satisfied
            remaining_reqs = self.novel.get_novel_requirements()
            print(
                f"Remaining novel requirements: {[req.value for req in remaining_reqs]}"
            )
        else:
            print("No valid updates from setup result:", result)

    async def ingest_chapter(
        self, chapter_index: int, chapter_text: str
    ) -> Dict[str, any]:
        """
        Runs the ingestion workflow to extract entities and relationships from a chapter

        Args:
            chapter_index: Index of the chapter
            chapter_text: Text content of the chapter

        Returns:
            Dictionary containing ingestion results (entities and triplets)
        """
        ingestion_workflow = self._get_or_create_ingestion_workflow()
        ingestion_state = IngestionState(
            text=chapter_text, entities=[], new_entities=[], triplets=[]
        )

        result = await ingestion_workflow.ainvoke(ingestion_state)

        # Mark chapter as ingested
        if chapter_index in self.novel.indexed_chapters:
            self.novel.indexed_chapters[chapter_index].ingested_status = True

        return result

    async def translate_chapter(
        self, chapter_index: int, chapter_text: str
    ) -> Dict[str, any]:
        """
        Runs the translation workflow to translate a chapter

        Args:
            chapter_index: Index of the chapter
            chapter_text: Text content of the chapter

        Returns:
            Dictionary containing translation results
        """
        translation_workflow = self._get_or_create_translation_workflow()
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

        # Update chapter with translation
        if chapter_index in self.novel.indexed_chapters:
            chapter = self.novel.indexed_chapters[chapter_index]
            chapter.translation = result.get(
                "fluent_translation", result.get("translation", "")
            )

        return result

    async def process_novel_completely(self, sample_text: str) -> Dict[str, any]:
        """
        Processes the entire novel through all three workflows

        Args:
            sample_text: Sample text for initial setup analysis

        Returns:
            Dictionary containing processing summary
        """
        results = {
            "setup": None,
            "chapters_processed": 0,
            "ingestions": [],
            "translations": [],
        }

        # Step 1: Setup phase
        print("Running setup workflow...")
        setup_result = await self.setup_novel(sample_text)
        results["setup"] = setup_result

        # Step 2 & 3: Process each chapter (ingestion + translation)
        for chapter_index, chapter in self.novel.indexed_chapters.items():
            print(f"Processing chapter {chapter_index}...")

            # Ingestion
            if not chapter.ingested_status:
                print(f"  Running ingestion for chapter {chapter_index}")
                ingestion_result = await self.ingest_chapter(
                    chapter_index, chapter.original
                )
                results["ingestions"].append(
                    {"chapter_index": chapter_index, "result": ingestion_result}
                )

            # Translation
            if chapter.translation is None:
                print(f"  Running translation for chapter {chapter_index}")
                translation_result = await self.translate_chapter(
                    chapter_index, chapter.original
                )
                results["translations"].append(
                    {"chapter_index": chapter_index, "result": translation_result}
                )

            results["chapters_processed"] += 1

        return results

    async def get_next_task(self) -> Optional[tuple]:
        """
        Gets the next pending task for the novel using the Novel's built-in task system

        Returns:
            Tuple of (chapter_index, chapter_text, requirement) or None if no tasks pending
        """
        return self.novel.get_task()

    async def process_next_task(
        self, sample_text: str = None
    ) -> Optional[Dict[str, any]]:
        """
        Processes the next pending task for the novel

        Args:
            sample_text: Sample text for setup tasks (required for novel-level requirements)

        Returns:
            Dictionary containing task results or None if no tasks pending
        """
        task = await self.get_next_task()
        if not task:
            return None

        chapter_index, chapter_text, requirement = task

        # Handle novel-level vs chapter-level tasks
        if chapter_index == -1:
            print(f"Processing novel-level task: {requirement.value}")
            # Novel-level task - use provided chapter_text as sample or sample_text parameter
            text_to_use = sample_text if sample_text else chapter_text
            if requirement in [
                Requirement.STYLE_GUIDE,
                Requirement.GENRES,
                Requirement.LANGUAGE,
            ]:
                # Process single requirement to avoid getting stuck
                return await self.process_single_setup_requirement(
                    text_to_use, requirement
                )
            else:
                raise NotImplementedError(
                    f"Novel-level task type {requirement.value} not implemented"
                )
        else:
            print(f"Processing task: {requirement.value} for chapter {chapter_index}")
            # Chapter-level task
            match requirement:
                case Requirement.SUMMARY:
                    self.novel.indexed_chapters[
                        chapter_index
                    ].summary = "holder_summary"
                    return {
                        "summary": "holder_summary"
                    }  # for now not implemented, consider integrating into ingestion
                case Requirement.INGESTION:
                    return await self.ingest_chapter(chapter_index, chapter_text)
                case Requirement.ANNOTATION:
                    # holder for now
                    self.novel.indexed_chapters[chapter_index].annotated_status = True
                    return
                case Requirement.TRANSLATION:
                    return await self.translate_chapter(chapter_index, chapter_text)
                case _:
                    raise NotImplementedError(
                        f"Chapter-level task type {requirement.value} not implemented"
                    )

    def get_novel_status(self) -> Dict[str, any]:
        """
        Gets the current status of the novel processing

        Returns:
            Dictionary containing novel processing status
        """
        total_chapters = len(self.novel.indexed_chapters)
        ingested_chapters = sum(
            1 for ch in self.novel.indexed_chapters.values() if ch.ingested_status
        )
        translated_chapters = sum(
            1
            for ch in self.novel.indexed_chapters.values()
            if ch.translation is not None
        )

        return {
            "total_chapters": total_chapters,
            "setup_complete": len(self.novel.get_novel_requirements()) == 0,
            "ingested_chapters": ingested_chapters,
            "translated_chapters": translated_chapters,
            "completion_percentage": {
                "ingestion": (ingested_chapters / total_chapters * 100)
                if total_chapters > 0
                else 0,
                "translation": (translated_chapters / total_chapters * 100)
                if total_chapters > 0
                else 0,
            },
            "novel_metadata": {
                "style_guide_set": self.novel.style_guide is not None,
                "genres_detected": self.novel.genres,
                "language_detected": self.novel.language,
            },
        }

    def _get_or_create_setup_workflow(self, requirements: List[Requirement]) -> Any:
        """
        Get or create setup workflow with caching

        Args:
            requirements: List of setup requirements

        Returns:
            Compiled setup workflow
        """
        # Create cache key based on requirements
        cache_key = f"setup_{'_'.join(req.value for req in sorted(requirements, key=lambda x: x.value))}"

        if cache_key not in self._workflow_cache:
            self._workflow_cache[cache_key] = (
                self.setup_workflow_factory.create_workflow(requirements)
            )

        return self._workflow_cache[cache_key]

    def _get_or_create_ingestion_workflow(self) -> Any:
        """
        Get or create ingestion workflow with caching

        Returns:
            Compiled ingestion workflow
        """
        cache_key = "ingestion"

        if cache_key not in self._workflow_cache:
            self._workflow_cache[cache_key] = (
                self.ingestion_workflow_factory.create_workflow()
            )

        return self._workflow_cache[cache_key]

    def _get_or_create_translation_workflow(self) -> Any:
        """
        Get or create translation workflow with caching

        Returns:
            Compiled translation workflow
        """
        cache_key = "translation"

        if cache_key not in self._workflow_cache:
            self._workflow_cache[cache_key] = (
                self.translation_workflow_factory.create_workflow()
            )

        return self._workflow_cache[cache_key]

    def clear_workflow_cache(self):
        """Clear the workflow cache"""
        self._workflow_cache.clear()

    def get_cache_info(self) -> Dict[str, int]:
        """
        Get information about cached workflows

        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_workflows": len(self._workflow_cache),
            "cache_keys": list(self._workflow_cache.keys()),
        }

    async def process_single_setup_requirement(
        self, text: str, requirement: Requirement
    ) -> Dict[str, any]:
        """
        Process a single setup requirement

        Args:
            text: Sample text for analysis
            requirement: The specific requirement to process

        Returns:
            Dictionary containing the setup result for this requirement
        """
        print(f"Processing single setup requirement: {requirement.value}")

        setup_workflow = self._get_or_create_setup_workflow([requirement])
        setup_state = SetupState(
            text=text,
            language="",  # SetupState expects string, not None
            genres=[],  # SetupState expects list, not None
            style_guide="",  # SetupState expects string, not None
        )

        print(
            f"Input state: text={len(setup_state['text'])} chars, language='{setup_state['language']}', genres={setup_state['genres']}, style_guide='{setup_state['style_guide']}'"
        )

        result = await setup_workflow.ainvoke(setup_state)

        # Update novel state immediately
        self._update_novel_from_setup_result(result)

        return result

    def get_all_pending_requirements(self) -> Dict[str, List[Requirement]]:
        """
        Get all pending requirements for the novel, organized by type

        Returns:
            Dictionary with novel-level and chapter-level requirements
        """
        novel_reqs = self.novel.get_novel_requirements()

        chapter_reqs = {}
        for chapter_idx, chapter in self.novel.indexed_chapters.items():
            reqs = chapter.get_requirements()
            if reqs:
                chapter_reqs[chapter_idx] = reqs

        return {
            "novel_requirements": novel_reqs,
            "chapter_requirements": chapter_reqs,
            "total_pending": len(novel_reqs)
            + sum(len(reqs) for reqs in chapter_reqs.values()),
        }
