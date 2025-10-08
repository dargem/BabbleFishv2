"""Registry for managing and organizing translation workflows"""

from typing import Dict, List, Optional, Any
from enum import Enum
from src.core import Requirement
from src.workflows import (
    SetupWorkflowFactory,
    IngestionWorkflowFactory,
    TranslationWorkflowFactory,
)
from src.workflows.states import SetupState, IngestionState, TranslationState


class WorkflowType(Enum):
    """Types of workflows available in the system"""

    SETUP = "setup"
    INGESTION = "ingestion"
    TRANSLATION = "translation"
    ANNOTATION = "annotation"


class RequirementExecutionContext:
    """Context object containing information needed to execute a requirement"""

    def __init__(
        self,
        chapter_index: int,
        chapter_text: str,
        requirement_type: Requirement,
        novel_context: Optional[Dict[str, Any]] = None,
        all_chapters: Optional[List[str]] = None,
    ):
        self.chapter_index = chapter_index
        self.chapter_text = chapter_text
        self.requirement_type = requirement_type
        self.novel_context = novel_context or {}
        self.all_chapters = all_chapters or []


class WorkflowRegistry:
    """Enhanced registry for managing workflow creation and execution"""

    def __init__(
        self,
        setup_factory: SetupWorkflowFactory,
        ingestion_factory: IngestionWorkflowFactory,
        translation_factory: TranslationWorkflowFactory,
    ):
        """
        Initialize workflow registry with specific workflow factories

        Args:
            setup_factory: Factory for creating setup workflows
            ingestion_factory: Factory for creating ingestion workflows
            translation_factory: Factory for creating translation workflows
        """
        self.setup_factory = setup_factory
        self.ingestion_factory = ingestion_factory
        self.translation_factory = translation_factory
        self._workflow_cache: Dict[str, Any] = {}

        # Define requirement-to-workflow mapping
        self._requirement_workflow_map = {
            Requirement.SETUP: WorkflowType.SETUP,
            Requirement.INGESTION: WorkflowType.INGESTION,
            Requirement.TRANSLATION: WorkflowType.TRANSLATION,
            Requirement.ANNOTATION: WorkflowType.ANNOTATION,
            Requirement.SUMMARY: None,  # Handled directly, no workflow needed
        }

    def get_workflow_for_requirement(
        self, requirement: Requirement
    ) -> Optional[WorkflowType]:
        """
        Get the workflow type needed for a specific requirement

        Args:
            requirement: The requirement to process

        Returns:
            WorkflowType if workflow is needed, None if handled directly
        """
        return self._requirement_workflow_map.get(requirement)

    async def execute_requirement(
        self, context: RequirementExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute a requirement using the appropriate workflow

        Args:
            context: Execution context containing requirement details

        Returns:
            Dictionary containing the execution result
        """
        workflow_type = self.get_workflow_for_requirement(context.requirement_type)

        if workflow_type is None:
            # Handle requirements that don't need workflows (like SUMMARY)
            return await self._handle_direct_requirement(context)

        # Handle novel-level vs chapter-level requirements
        if context.chapter_index == -1:
            return await self._execute_novel_requirement(context, workflow_type)
        else:
            return await self._execute_chapter_requirement(context, workflow_type)

    async def _handle_direct_requirement(
        self, context: RequirementExecutionContext
    ) -> Dict[str, Any]:
        """Handle requirements that don't need a workflow"""
        if context.requirement_type == Requirement.SUMMARY:
            return {"summary": "Generated summary placeholder"}
        elif context.requirement_type == Requirement.ANNOTATION:
            return {"annotation": "completed"}
        else:
            raise NotImplementedError(
                f"Direct requirement handling for {context.requirement_type.value} not implemented"
            )

    async def _execute_novel_requirement(
        self, context: RequirementExecutionContext, workflow_type: WorkflowType
    ) -> Dict[str, Any]:
        """Execute a novel-level requirement"""
        if workflow_type != WorkflowType.SETUP:
            raise ValueError(
                f"Novel-level requirements must use SETUP workflow, got {workflow_type}"
            )

        workflow = self.get_workflow(WorkflowType.SETUP)
        state = SetupState(
            text=context.chapter_text or "",
            all_chapters=context.all_chapters or [],
            language="",  # Will be detected by workflow
            genres=[],  # Will be detected by workflow
            style_guide="",  # Will be analyzed by workflow
            tags=[],  # Will be generated by workflow
        )

        return await workflow.ainvoke(state)

    async def _execute_chapter_requirement(
        self, context: RequirementExecutionContext, workflow_type: WorkflowType
    ) -> Dict[str, Any]:
        """Execute a chapter-level requirement"""
        match workflow_type:
            case WorkflowType.INGESTION:
                workflow = self.get_workflow(WorkflowType.INGESTION)
                state = IngestionState(
                    text=context.chapter_text, entities=[], new_entities=[], triplets=[]
                )
                return await workflow.ainvoke(state)

            case WorkflowType.TRANSLATION:
                workflow = self.get_workflow(WorkflowType.TRANSLATION)
                state = TranslationState(
                    text=context.chapter_text,
                    style_guide=context.novel_context.get("style_guide", ""),
                    language=context.novel_context.get("language", ""),
                    translation="",
                    fluent_translation="",
                    feedback="",
                    feedback_rout_loops=0,
                )
                return await workflow.ainvoke(state)

            case WorkflowType.ANNOTATION:
                # TODO: Implement annotation workflow when factory is available
                return {"annotation": "completed"}

            case _:
                raise ValueError(
                    f"Unknown workflow type for chapter requirement: {workflow_type}"
                )

    def get_workflow(self, workflow_type: WorkflowType, **kwargs) -> Any:
        """
        Get a workflow instance, with caching for performance

        Args:
            workflow_type: Type of workflow to create
            **kwargs: Additional parameters for workflow creation

        Returns:
            Compiled workflow instance
        """
        cache_key = self._get_cache_key(workflow_type, **kwargs)

        if cache_key in self._workflow_cache:
            return self._workflow_cache[cache_key]

        workflow = self._create_workflow(workflow_type, **kwargs)
        self._workflow_cache[cache_key] = workflow

        return workflow

    def _create_workflow(self, workflow_type: WorkflowType, **kwargs) -> Any:
        """
        Create a new workflow instance

        Args:
            workflow_type: Type of workflow to create
            **kwargs: Additional parameters for workflow creation

        Returns:
            Compiled workflow instance
        """
        match workflow_type:
            case WorkflowType.SETUP:
                return self.setup_factory.create_workflow()

            case WorkflowType.INGESTION:
                return self.ingestion_factory.create_workflow()

            case WorkflowType.TRANSLATION:
                return self.translation_factory.create_workflow()

            case WorkflowType.ANNOTATION:
                # TODO: Implement annotation workflow when factory is available
                return {"annotation": "workflow not implemented yet"}

            case _:
                raise ValueError(f"Unknown workflow type: {workflow_type}")

    def get_requirements_for_workflow(
        self, workflow_type: WorkflowType
    ) -> List[Requirement]:
        """
        Get all requirements that use a specific workflow type

        Args:
            workflow_type: The workflow type to query

        Returns:
            List of requirements that use this workflow
        """
        return [
            req
            for req, wf_type in self._requirement_workflow_map.items()
            if wf_type == workflow_type
        ]

    def get_all_workflow_types(self) -> List[WorkflowType]:
        """Get all available workflow types"""
        return list(WorkflowType)

    def get_all_requirements(self) -> List[Requirement]:
        """Get all supported requirements"""
        return list(self._requirement_workflow_map.keys())

    def _get_cache_key(self, workflow_type: WorkflowType, **kwargs) -> str:
        """
        Generate cache key for workflow instances

        Args:
            workflow_type: Type of workflow
            **kwargs: Additional parameters (currently unused)

        Returns:
            Cache key string
        """
        # Since all workflows now take no parameters, cache key is just the workflow type
        return workflow_type.value

    def clear_cache(self):
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

    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all workflow dependencies

        Returns:
            Dictionary with health status of each workflow type
        """
        results = {}

        try:
            # Test setup workflow
            setup_wf = self.get_workflow(WorkflowType.SETUP)
            results[WorkflowType.SETUP.value] = setup_wf is not None
        except Exception:
            results[WorkflowType.SETUP.value] = False

        try:
            # Test ingestion workflow
            ingestion_wf = self.get_workflow(WorkflowType.INGESTION)
            results[WorkflowType.INGESTION.value] = ingestion_wf is not None
        except Exception:
            results[WorkflowType.INGESTION.value] = False

        try:
            # Test translation workflow
            translation_wf = self.get_workflow(WorkflowType.TRANSLATION)
            results[WorkflowType.TRANSLATION.value] = translation_wf is not None
        except Exception:
            results[WorkflowType.TRANSLATION.value] = False

        return results
