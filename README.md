# BabbleFishv2

Agentic translation system, an attempted implementation of (Perhaps) Beyond Human Translation: Harnessing Multi-Agent Collaboration for Translating Ultra-Long Literary Texts. https://arxiv.org/html/2405.11804v1. Aided with Graphiti inspired graphRAG using temporal chapter based memory, WIP.

## Features
- **Knowledge Graphs**: Uses Neo4j to map triplets and entities into a graphical database
- **Feedback Loops**: LLM based feedback loops for reviewing
- **Workflow Visualization**: Generates Mermaid diagrams of the process

## Current pipeline
Setup Phase:
- **Language detection** Lingua for detection
- **Styleguide Creation** Creates a styleguide for future translation
- **Genre Tagging** Tags text with choices from the set genre enum
- **TODO Topic Tags** Use some topic modelling approach

Ingestion Phase:
- **Entity Extraction** LLM for categorised NER
- **Triplet Extraction** Temporally and metadata tagged triplet extraction using fixed predicate enums
- **TODO Tuple Extraction** For tuples since relations may be with themselves, e.g. traits

Annotation Phase:
- **Entity Replacer** Tags a recognised entity in the text with its match in translation memory
- **WIP** Add an agent with some tool use for the database

Translation Phase:
- **Translation** Translation with gemini
- **Junior Editor**: Feedback on translation input, can reject up to 3 times
- **Fluency Editor**: Base text blind index based editing for fluency

## TODO
- Possibly make a SQL database
- Integrate a web scraper or make one myself
- Novel factory, takes in text dicts to produce them, probably abstracts loading from epub, txt etc
- Tagging using corextopic for topic modelling, potentially seed it then use llm to classify topics
- Try other approaches with keyword extraction after preprocessing
- Maybe change the nodes to all be an implementation of an abstract class for more consistency
- Embeddings with entity descriptions
- More database queries BM25, community clustering, etc
- Setup phase creates domain specific edge types
- DB query agent for informing translations
- agent profiles 
- langsmith or similar for some evaluations on unit tests
- Include batch processing capabilities
- Add metrics and monitoring
- Implement different editorial personas, probably need to abstract nodes using a registry for this
- Fix github workflow
- Add tests
- 2 fold triplet extraction, also for attribute based triplets (or tuples maybe is more accurate?)
- Funny entity resolution bug, A changed his name to B, B has coreference resolution with A so triplet reads as A changed to A
- Add custom Japanese + Korean lemmatiser spacy doesn't have, Chinese doesn't need it

## Ticked Off
- Create nlp provider which does language configurable POS tagging, lemmatisation etc for preprocessing
- Logging
- Abstract class workflow factories inherit from
- Entity replacer to substitute in Translation Memory Joshua -> Joshua \[Translation Memory 约书亚\]
- Architecturally novel processor feels like a mess, remake it
- Translation Orchestrator
- Get a better prompt so it stops screwing up predicates
- Entity unification
- Informative relation based triplet extraction
- change architecture, 4 workflows,
    - setup (get language, style guide etc), 
    - ingestion (get triplets into graphical database with localisations)
    - annotation (annotate the base text with references like translations etc)
    - translation (generic translation workflow with feedback loops etc)
- Registry for the translation orchestrator