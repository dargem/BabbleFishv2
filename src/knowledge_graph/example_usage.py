"""Example usage of the knowledge graph system"""

from knowledge_graph import (
    KnowledgeGraphManager,
    KnowledgeGraphQuery,
    Entity,
    Triplet,
    EntityType,
    TripletMetadata,
    get_entity_summary,
    get_triplet_summary
)


def example_usage():
    """Demonstrate knowledge graph operations"""
    
    # Initialize the knowledge graph manager
    with KnowledgeGraphManager() as kg:
        
        # Create some example entities
        entities = [
            Entity(
                names=["Harry Potter", "Harry", "The Boy Who Lived"],
                entity_type=EntityType.PERSON,
                translation="Гарри Поттер",
                description="A young wizard",
                chapter_idx=1,
                properties={"age": 11, "house": "Gryffindor"}
            ),
            Entity(
                names=["Hermione Granger", "Hermione"],
                entity_type=EntityType.PERSON,
                translation="Гермиона Грейнджер", 
                description="A brilliant witch",
                chapter_idx=1,
                properties={"age": 11, "house": "Gryffindor"}
            ),
            Entity(
                names=["Hogwarts", "Hogwarts School"],
                entity_type=EntityType.PLACE,
                description="School of Witchcraft and Wizardry",
                chapter_idx=1
            ),
            Entity(
                names=["Elder Wand", "The Elder Wand"],
                entity_type=EntityType.ITEM,
                description="One of the Deathly Hallows",
                chapter_idx=5
            )
        ]
        
        # Add entities to the knowledge graph
        print("Adding entities...")
        created_count = kg.add_entities(entities)
        print(f"Created {created_count} entities")
        
        # Create some triplets/relationships
        triplets = [
            Triplet(
                subject_name="Harry Potter",
                predicate="FRIENDS_WITH",
                object_name="Hermione Granger",
                metadata=TripletMetadata(
                    chapter_idx=1,
                    temporal_type="dynamic",
                    statement_type="fact",
                    confidence=0.95,
                    source_text="Harry and Hermione became close friends"
                )
            ),
            Triplet(
                subject_name="Harry Potter",
                predicate="ATTENDS",
                object_name="Hogwarts",
                metadata=TripletMetadata(
                    chapter_idx=1,
                    temporal_type="dynamic",
                    statement_type="fact",
                    confidence=1.0
                )
            ),
            Triplet(
                subject_name="Harry Potter",
                predicate="POSSESSES",
                object_name="Elder Wand",
                metadata=TripletMetadata(
                    chapter_idx=5,
                    temporal_type="dynamic",
                    statement_type="fact",
                    confidence=0.9,
                    source_text="Harry became the master of the Elder Wand"
                )
            )
        ]
        
        # Add triplets to the knowledge graph
        print("Adding triplets...")
        triplet_count = kg.add_triplets(triplets)
        print(f"Created {triplet_count} relationships")
        
        # Query operations
        query_interface = KnowledgeGraphQuery(kg)
        
        # Find entity by name
        print("\nFinding Harry Potter...")
        harry = kg.find_entity_by_name("Harry")
        if harry:
            print(f"Found: {harry}")
        
        # Get all relationships for Harry Potter
        print("\nHarry's relationships:")
        relationships = kg.get_entity_relationships("Harry Potter")
        for rel in relationships:
            print(f"  {rel}")
        
        # Get entities by type
        print("\nAll Person entities:")
        people = kg.get_entities_by_type(EntityType.PERSON)
        for person in people:
            entity = Entity(
                names=person["names"],
                entity_type=EntityType(person["entity_type"]),
                translation=person.get("translation"),
                description=person.get("description"),
                chapter_idx=person.get("chapter_idx")
            )
            print(f"  {get_entity_summary(entity)}")
        
        # Get triplets from a specific chapter
        print(f"\nRelationships from chapter 1:")
        chapter1_triplets = kg.get_triplets_by_chapter(1)
        for triplet_data in chapter1_triplets:
            print(f"  {triplet_data['subject_names'][0]} -[{triplet_data['predicate']}]-> {triplet_data['object_names'][0]}")
        
        # Get connected entities
        print("\nEntities connected to Harry Potter:")
        connected = query_interface.find_connected_entities("Harry Potter", max_depth=2)
        for conn in connected:
            entity_names = conn["entity"]["names"]
            distance = conn["distance"]
            print(f"  {entity_names[0]} (distance: {distance})")
        
        # Get character interactions
        print("\nCharacter interactions:")
        interactions = query_interface.get_character_interactions()
        for interaction in interactions:
            person1_names = interaction["person1"]["names"]
            person2_names = interaction["person2"]["names"]
            predicate = interaction["interaction"]["predicate"]
            print(f"  {person1_names[0]} -[{predicate}]-> {person2_names[0]}")
        
        # Get narrative graph for chapter 1
        print("\nChapter 1 narrative graph:")
        narrative = query_interface.get_chapter_narrative_graph(1)
        print(f"  Entities: {narrative['entity_count']}")
        print(f"  Relationships: {narrative['relationship_count']}")
        
        # Get database statistics
        print("\nDatabase statistics:")
        stats = kg.get_stats()
        print(f"  Total entities: {stats['entities']}")
        print(f"  Total relationships: {stats['relationships']}")


if __name__ == "__main__":
    example_usage()
