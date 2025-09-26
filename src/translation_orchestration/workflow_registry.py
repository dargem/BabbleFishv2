"""Registry for managing and organizing translation workflows"""

from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from src.core import Requirement
from src.workflows import (
    SetupWorkflowFactory,
    IngestionWorkflowFactory,
    TranslationWorkflowFactory,
)


class WorkflowType(Enum):
    """Types of workflows available in the system"""

    SETUP = "setup"
    INGESTION = "ingestion"
    TRANSLATION = "translation"


class WorkflowRegistry:
    """Registry for managing workflow creation and execution"""

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
                requirements = kwargs.get("requirements", [])
                return self.setup_factory.create_workflow(requirements)

            case WorkflowType.INGESTION:
                return self.ingestion_factory.create_workflow()

            case WorkflowType.TRANSLATION:
                return self.translation_factory.create_workflow()

            case _:
                raise ValueError(f"Unknown workflow type: {workflow_type}")

    def _get_cache_key(self, workflow_type: WorkflowType, **kwargs) -> str:
        """
        Generate cache key for workflow instances

        Args:
            workflow_type: Type of workflow
            **kwargs: Additional parameters

        Returns:
            Cache key string
        """
        key_parts = [workflow_type.value]

        if workflow_type == WorkflowType.SETUP and "requirements" in kwargs:
            # Sort requirements for consistent cache keys
            req_names = sorted([req.value for req in kwargs["requirements"]])
            key_parts.extend(req_names)

        return "|".join(key_parts)

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

    def get_available_workflows(self) -> List[WorkflowType]:
        """
        Get list of available workflow types

        Returns:
            List of available workflow types
        """
        return list(WorkflowType)

    def get_setup_requirements(self) -> List[Requirement]:
        """
        Get list of available setup requirements

        Returns:
            List of setup requirements that can be used
        """
        return [Requirement.STYLE_GUIDE, Requirement.GENRES, Requirement.LANGUAGE]

    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all workflow dependencies

        Returns:
            Dictionary with health status of each workflow type
        """
        results = {}

        try:
            # Test setup workflow with minimal requirements
            setup_wf = self.get_workflow(
                WorkflowType.SETUP, requirements=[Requirement.LANGUAGE]
            )
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


class WorkflowExecutor:
    """Helper class for executing workflows with common patterns"""

    def __init__(self, registry: WorkflowRegistry):
        """
        Initialize workflow executor

        Args:
            registry: Workflow registry instance
        """
        self.registry = registry

    async def execute_setup_workflow(
        self, text: str, requirements: List[Requirement]
    ) -> Dict[str, Any]:
        """
        Execute setup workflow with given requirements

        Args:
            text: Input text for analysis
            requirements: List of setup requirements

        Returns:
            Dictionary with setup results
        """
        from src.workflows.states import SetupState

        workflow = self.registry.get_workflow(
            WorkflowType.SETUP, requirements=requirements
        )
        state = SetupState(text=text)

        return await workflow.ainvoke(state)

    async def execute_ingestion_workflow(self, text: str) -> Dict[str, Any]:
        """
        Execute ingestion workflow

        Args:
            text: Input text for entity and relationship extraction

        Returns:
            Dictionary with ingestion results
        """
        from src.workflows.states import IngestionState

        workflow = self.registry.get_workflow(WorkflowType.INGESTION)
        state = IngestionState(text=text, entities=[], new_entities=[], triplets=[])

        return await workflow.ainvoke(state)

    async def execute_translation_workflow(
        self, text: str, style_guide: str = "", language: str = ""
    ) -> Dict[str, Any]:
        """
        Execute translation workflow

        Args:
            text: Input text for translation
            style_guide: Style guide for translation consistency
            language: Source language

        Returns:
            Dictionary with translation results
        """
        from src.workflows.states import TranslationState

        workflow = self.registry.get_workflow(WorkflowType.TRANSLATION)
        state = TranslationState(
            text=text,
            style_guide=style_guide,
            language=language,
            translation="",
            fluent_translation="",
            feedback="",
            feedback_rout_loops=0,
        )

        return await workflow.ainvoke(state)
