"""Factories for workflows"""

from abc import ABC, abstractmethod

class AbstractWorkflowFactory(ABC):
    """
    The abstract class for all workflow factories
    """
    @abstractmethod
    def create_workflow(self):
        pass