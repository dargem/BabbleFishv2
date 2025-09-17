# BabbleFishv2

Agentic translation system, an attempted implementation of (Perhaps) Beyond Human Translation: Harnessing Multi-Agent Collaboration for Translating Ultra-Long Literary Texts. https://arxiv.org/html/2405.11804v1. Aided with Graphiti inspired graphRAG using temporal chapter based memory, WIP.

## Features
- **Knowledge Graphs**: Uses Neo4j to map triplets and entities into a graphical database
- **Feedback Loops**: LLM based feedback loops for reviewing
- **Workflow Visualization**: Generates Mermaid diagrams of the process

Current pipeline
- **Entity Extraction** LLM for categorised NER
- **Triplet Extraction** Temporally and metadata tagged triplet extraction using fixed predicate enums
- **Styleguide Creation** Creates a styleguide for future translation
- **Language detection** Lingua for detection
- **Translation** Translation with gemini
- **Junior Editor**: Feedback on translation input, can reject up to 3 times
- **Fluency Editor**: Base text blind index based editing for fluency

## TODO
- Embeddings with entity descriptions
- Community clustering
- Setup phase creates domain specific edge types
- Node based knowledge *maybe bad design actually
- DB query agent for informing translations
- Integrate in better edge types, Setup phase can create piece specific relationships
- Get a better prompt so it stops screwing up predicates
- Enforce better edge detection and node unification
- Entity unification
- change architecture, 3 workflows,
    - setup (get language, style guide etc), 
    - ingestion (get triplets into graphical database with localisations) status: Partially done
    - translation (generic translation workflow with feedback loops etc) status: Partially done
- agent profiles 
- langsmith or similar for some evaluations on unit tests
- Include batch processing capabilities
- Add metrics and monitoring
- Implement different editorial personas, probably need to abstract nodes using a registry for this
- Abstract nodes using a registry pattern
- Fix github workflow
- 2 fold triplet extraction, one of attributes and one of inter entity relations