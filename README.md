# BabbleFishv2

Attempted implementation of 
(Perhaps) Beyond Human Translation: Harnessing Multi-Agent Collaboration for Translating Ultra-Long Literary Texts
https://arxiv.org/html/2405.11804v1
Paired with graphiti for some temporal chapter based memory, WIP.


Translation system using LangGraph and LangChain with iterative feedback loops and fluency optimization.
Agentic memory through graphRAG using graphiti to build entities + relationship database with neo4j.
Uses Gemini

## Features

- **Feedback Loops**: LLM based feedback loops for reviewing
- **Workflow Visualization**: Generates Mermaid diagrams of the process

Current pipeline
- **Language detection** Lingua for detection
- **Translation** Translation with gemini
- **Junior Editor**: Feedback on translation input, can reject up to 3 times
- **Fluency Editor**: Base text blind index based editing for fluency

## TODO

- agent profiles 
- graphiti for memory
- customise graphiti, addition removal agent etc
- unit tests, probably langsmith for some evaluations
- Include batch processing capabilities
- Add metrics and monitoring
- Implement different editorial personas
- Add novel level style guides