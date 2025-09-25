# BabbleFishv2

Agentic translation system, an attempted implementation of (Perhaps) Beyond Human Translation: Harnessing Multi-Agent Collaboration for Translating Ultra-Long Literary Texts. https://arxiv.org/html/2405.11804v1. Aided with Graphiti inspired graphRAG using temporal chapter based memory, WIP.

## Features
- **Knowledge Graphs**: Uses Neo4j to map triplets and entities into a graphical database
- **Feedback Loops**: LLM based feedback loops for reviewing
- **Workflow Visualization**: Generates Mermaid diagrams of the process

## Current pipeline
Setup Phase:
- **WIP** Will move styleguide, language detection and create domain specific enums soon

Ingestion Phase:
- **Entity Extraction** LLM for categorised NER
- **Triplet Extraction** Temporally and metadata tagged triplet extraction using fixed predicate enums

Translation Phase:
- **Styleguide Creation** Creates a styleguide for future translation
- **Language detection** Lingua for detection
- **Translation** Translation with gemini
- **Junior Editor**: Feedback on translation input, can reject up to 3 times
- **Fluency Editor**: Base text blind index based editing for fluency

## TODO
- Some kindof non llm based topic modelling, maybe like latent dirichlet allocation?
- Maybe change the nodes to all be an implementation of an abstract class
- Translation Orchestrator
- Registry for the translation orchestrator
- Embeddings with entity descriptions
- More database queries BM25, community clustering, etc
- Setup phase creates domain specific edge types
- DB query agent for informing translations
- Integrate in better edge types, Setup phase can create piece specific relationships
- Enforce better edge detection and node unification
- change architecture, 4 workflows,
    - setup (get language, style guide etc), 
    - ingestion (get triplets into graphical database with localisations) status: Partially done
    - annotation (annotate the base text with references like translations etc)
    - translation (generic translation workflow with feedback loops etc) status: Partially done
- agent profiles 
- langsmith or similar for some evaluations on unit tests
- Include batch processing capabilities
- Add metrics and monitoring
- Implement different editorial personas, probably need to abstract nodes using a registry for this
- Abstract nodes using a registry pattern
- Fix github workflow
- 2 fold triplet extraction, also for attribute based triplets (or tuples maybe is more accurate?)
- Funny entity resolution bug, A changed his name to B, B has coreference resolution with A so triplet reads as A changed to A

## Ticked Off
- Get a better prompt so it stops screwing up predicates
- Entity unification
- Informative relation based triplet extraction