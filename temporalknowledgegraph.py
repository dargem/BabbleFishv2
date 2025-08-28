"""
Test on creating temporal knowledge graphs cooked up from this
https://cookbook.openai.com/examples/partners/temporal_agents_with_knowledge_graphs/temporal_agents_with_knowledge_graphs#2-how-to-use-this-cookbook



Input text

named entity recognition + unification
    - Could use fuzzy match for unification then just merge them, seems error prone especially over long novels
    - LLM based merge, then unify against existing data. Shouldn't lead to a bad merge resulting in chain merging which could be very bad.
    - Could probably be its own stage


triplet extraction
    - subject predicate object
    with metadata
    temporal validation labels it as one of the following:
        - Atemporal (never changing, Jill is the sister of Bob)
        - Static (Valid from a point, not changing afterwards, Bob was alive on the 23rd of January, could change later)
        - Dynamic (Changing statements which are evolving, Bob is in Hillsbury. This should "expire")
    statement types:
        - Fact (verifiably true at the time of claim)
        - Opinion (subjectively true considering the speakers judgement)
        - Prediction (Forward looking hypothetical about a potential future event) *prediction probably not needed
    temporal extraction
        - Log by chapter
        - Possible error with a flashback, etc or referring to past events
        - May have difficulties as can't resolve to a date
        - Probably filter to exclude by llm?

Invalidation agent (replace old relationships with new ones if applicable)
Option to not use invalidation agent, doing it at recall to save api calls
"""


