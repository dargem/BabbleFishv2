# # BabbleFish Translation System

A sophisticated Chinese to English translation system using LangGraph and LangChain with iterative feedback loops and fluency optimization.

## Project Structure

```
BabbleFishv2/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── main_refactored.py       # Main application module
│   ├── models/                  # Data models and state definitions
│   │   └── __init__.py          # TranslationState model
│   ├── config/                  # Configuration management
│   │   └── __init__.py          # Config class and LLM setup
│   ├── nodes/                   # Workflow nodes
│   │   ├── __init__.py          # Node exports
│   │   ├── language_detection.py  # Language detection logic
│   │   ├── translation.py       # Translation logic
│   │   ├── editing.py           # Editorial nodes
│   │   └── routing.py           # State management nodes
│   ├── workflow/                # Workflow definition
│   │   └── __init__.py          # Graph creation and routing logic
│   └── utils/                   # Utility functions
│       └── __init__.py          # Text processing utilities
├── run_translation.py           # Main entry point script
├── main_refactored.py           # Original entry point (kept for compatibility)
├── main.py                      # Original monolithic file
└── requirements.txt             # Dependencies
```

## Features

- **Language Detection**: Automatically detects the source language
- **Professional Translation**: Specialized for Chinese fiction to English
- **Quality Assurance**: Junior editor provides feedback on translations
- **Iterative Improvement**: Up to 3 feedback loops for refinement
- **Fluency Optimization**: Final pass for narrative flow and readability
- **Workflow Visualization**: Generates Mermaid diagrams of the process

## Usage

Run the translation system:
```bash
# Option 1: Use the main entry point
python run_translation.py

# Option 2: Use the original file (still works)
python main_refactored.py

# Option 3: Run from within src directory
cd src && python -m main_refactored
```

## Architecture Benefits

1. **Modularity**: Each component has a specific responsibility
2. **Scalability**: Easy to add new nodes or modify existing ones
3. **Testability**: Individual components can be tested in isolation
4. **Maintainability**: Clear separation of concerns
5. **Extensibility**: Simple to add new language pairs or editing strategies

## Next Steps for Growth

- Add support for multiple language pairs
- Implement different translation strategies
- Add caching mechanisms
- Include batch processing capabilities
- Add metrics and monitoring
- Implement different editorial personas
- Add custom style guides

# BabbleFishv2