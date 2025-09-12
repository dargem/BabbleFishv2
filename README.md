# BabbleFishv2

Agentic translation system, an attempted implementation of (Perhaps) Beyond Human Translation: Harnessing Multi-Agent Collaboration for Translating Ultra-Long Literary Texts. https://arxiv.org/html/2405.11804v1. Aided with Graphiti inspired graphRAG using temporal chapter based memory, WIP.

## Features
- **Graphical Database**: Facade created, interfaces neo4j
- **Feedback Loops**: LLM based feedback loops for reviewing
- **Workflow Visualization**: Generates Mermaid diagrams of the process

Current pipeline
- **Styleguide Creation** Creates a styleguide for future translation
- **Language detection** Lingua for detection
- **Translation** Translation with gemini
- **Junior Editor**: Feedback on translation input, can reject up to 3 times
- **Fluency Editor**: Base text blind index based editing for fluency

## TODO
- Setup phase creates domain specific edge types
- Integrate in better edge types
- Enforce better edge detection and node unification
- change architecture, 3 workflows,
    - setup (get language, style guide etc), 
    - ingestion (get triplets into graphical database with localisations) status: Partially done
    - translation (generic translation workflow with feedback loops etc) status: Partially done
- agent profiles 
- langsmith for some evaluations on unit tests
- Include batch processing capabilities
- Add metrics and monitoring
- Implement different editorial personas
- Fix github workflow