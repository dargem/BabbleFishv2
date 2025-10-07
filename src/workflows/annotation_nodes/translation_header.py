"""
Creates a header for translations using found entities
Notes their attributes and relations with other entities
"""

from src.knowledge_graph import KnowledgeGraphManager
from src.workflows.states import AnnotationState
from typing import Dict, List
from flashtext import KeywordProcessor


class HeaderCreator:
    def __init__(self, kg: KnowledgeGraphManager):
        self.kg = kg

    def _get_matches(
        self, entity_name_lists: List[List[str]], text: str
    ) -> Dict[str, List[str]]:
        """
        Args:
            kp: Keyword processor object
            entity_names_list: A list of names from a list of entities

        Returns:
            Dict of list of names keyed by their base name
        """
        name_based = {}
        kp = KeywordProcessor()
        for name_list in entity_name_lists:
            base = name_list[0]
            for name in name_list:
                name_based[name] = base
                kp.add_keyword(name)
        matched = kp.get_all_keywords(text)
        # creates a dict of base names in one to many with their co-referencing names
        output_dic = {}
        for match in matched:
            if name_based[match] not in output_dic:
                output_dic[name_based[match]] = []
            output_dic[name_based[match]].append(match)
        return output_dic

    def create_header(self, state: AnnotationState) -> Dict[str, str]:
        """
        Creates a header for the translation incorporating the graphical knowledge-bases info

        Args:
            state: Current state of the translation

        Returns:
            Dict containing the header all in one value, entity info + relation info inside it
        """

        text = state["text"]
        entities = self.kg.get_all_entities()
        entity_name_lists: List[List[str]] = [entity.all_names for entity in entities]
        matches = self._get_matches(entity_name_lists, text)
