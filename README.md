# BabbleFishv2

Attempted implementation of 
(Perhaps) Beyond Human Translation: Harnessing Multi-Agent Collaboration for Translating Ultra-Long Literary Texts. https://arxiv.org/html/2405.11804v1. Aided with some Graphiti inspired graphRAG using a graph database with temporal chapter based.

temporal chapter based memory, WIP.


Translation system using LangGraph with iterative feedback loops and fluency optimization.
Agentic memory through graphRAG using graphiti to build entities + relationship database with neo4j.

## Features

- **Feedback Loops**: LLM based feedback loops for reviewing
- **Workflow Visualization**: Generates Mermaid diagrams of the process

Current pipeline
- **Styleguide Creation** Creates a styleguide for future translation
- **Language detection** Lingua for detection
- **Translation** Translation with gemini
- **Junior Editor**: Feedback on translation input, can reject up to 3 times
- **Fluency Editor**: Base text blind index based editing for fluency

## TODO

- change architecture, 3 workflows,
    - setup (get language, style guide etc), 
    - ingestion (get triplets into graphical database with localisations)
    - translation (generic translation workflow with feedback loops etc)
- agent profiles 
- temporal knowledge graphs for memory
- langsmith for some evaluations on unit tests
- Include batch processing capabilities
- Add metrics and monitoring
- Implement different editorial personas
- Fix github workflow