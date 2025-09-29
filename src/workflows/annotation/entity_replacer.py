"""
Adds annotated translation of a name entry into it, functions as translation memory
e.g. Joshua went to the store -> Joshua [Translation Memory 约书亚] went to the store
"""

from src.knowledge_graph import KnowledgeGraphManager
from src.workflows.states import AnnotationState
from flashtext import KeywordProcessor
from typing import List


class EntityAnnotator:
    def __init__(self, kg: KnowledgeGraphManager):
        self.kg = kg

    def inject_entity_translations(self, state: AnnotationState):
        """
        Replaces an entity with its suggestion translation
        Args:
            state: current annotation state of the text
        """
        kp = KeywordProcessor()
        entities = self.kg.get_all_entities()

        entity_name_translations: List[dict] = [
            entity.translations for entity in entities
        ]
        for dic in entity_name_translations:
            for name, translation in dic.items():
                # needs replacer else loses original
                replacer = f"{name} [Translation Memory {translation}]"
                kp.add_keyword(name, replacer)

        output = kp.replace_keywords(state["text"])
        return {"keyword_replaced_text": output}
