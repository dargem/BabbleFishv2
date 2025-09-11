# Migration Guide: Old Config → New Provider Architecture

This guide shows how to migrate from the old global config pattern to the new provider architecture.

## Key Changes

### 1. Replace Global Config Import

**Before:**
```python
from src.config import config

def translator_node(state):
    llm = config.get_llm()
    response = llm.invoke(messages)
    return {"translation": response}
```

**After:**
```python
from src.providers import LLMProvider

class TranslatorNode:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    async def translate(self, state):
        response = await self.llm_provider.invoke(messages)
        return {"translation": response}
```

### 2. Update Main Application Bootstrap

**Before:**
```python
# src/main.py
from src.config import config
from src.workflows import create_translation_workflow

def run_translation():
    kg = KnowledgeGraphManager()
    workflow = create_translation_workflow()
    result = workflow.invoke(state_input)
```

**After:**
```python
# src/main.py
import asyncio
from src.config import ConfigFactory, Container

async def run_translation():
    # Load environment-specific config
    config = ConfigFactory.create_config()
    
    # Set up dependency container
    container = Container()
    container.set_config(config)
    
    # Get dependencies
    llm_provider = container.get_llm_provider()
    kg_manager = container.get_knowledge_graph_manager()
    
    # Create workflow with injected dependencies
    workflow = create_translation_workflow(llm_provider, kg_manager)
    result = await workflow.run(state_input)

if __name__ == "__main__":
    asyncio.run(run_translation())
```

### 3. Update Workflow Creation

**Before:**
```python
# src/workflows/translation/workflow.py
def create_translation_workflow():
    workflow = StateGraph(TranslationState)
    workflow.add_node("translator_node", translator_node)
    # ...
    return workflow.compile()
```

**After:**
```python
# src/workflows/translation/workflow.py
def create_translation_workflow(llm_provider: LLMProvider, kg_manager: KnowledgeGraphManager):
    # Create nodes with injected dependencies
    translator = TranslatorNode(llm_provider)
    junior_editor = JuniorEditorNode(llm_provider)
    fluency_editor = FluencyEditorNode(llm_provider)
    
    workflow = StateGraph(TranslationState)
    workflow.add_node("translator_node", translator.translate)
    workflow.add_node("junior_editor_node", junior_editor.review)
    workflow.add_node("fluency_editor_node", fluency_editor.edit)
    # ...
    return workflow.compile()
```

### 4. Update Individual Nodes

**Before:**
```python
# src/workflows/translation/translator.py
from src.config import config

def translator_node(state: TranslationState) -> dict:
    print("Translating text...")
    llm = config.get_llm()
    # ... rest of function
```

**After:**
```python
# src/workflows/translation/translator.py
from src.providers import LLMProvider

class TranslatorNode:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    async def translate(self, state: TranslationState) -> dict:
        print("Translating text...")
        # ... build messages ...
        response = await self.llm_provider.invoke(messages)
        return {"translation": response.strip()}
```

### 5. Update Tests

**Before:**
```python
# tests/test_translator.py
from unittest.mock import Mock, patch
from src.workflows.translation.translator import translator_node

class TestTranslator(unittest.TestCase):
    @patch('src.config.config.get_llm')
    def test_translator(self, mock_get_llm):
        mock_llm = Mock()
        mock_llm.invoke.return_value = "Test translation"
        mock_get_llm.return_value = mock_llm
        
        result = translator_node({"text": "test", "language": "en"})
        self.assertEqual(result["translation"], "Test translation")
```

**After:**
```python
# tests/test_translator.py
import pytest
from src.workflows.translation.translator import TranslatorNode
from src.providers import MockLLMProvider

class TestTranslator:
    @pytest.mark.asyncio
    async def test_translator(self):
        # Use mock provider
        mock_provider = MockLLMProvider(responses=["Test translation"])
        translator = TranslatorNode(mock_provider)
        
        result = await translator.translate({"text": "test", "language": "en"})
        assert result["translation"] == "Test translation"
```

## Environment Variables Setup

Create a `.env` file in your project root:

```bash
# .env file
ENVIRONMENT=development

# Google API Keys (add as many as you have)
GOOGLE_API_KEY_1=your-first-api-key-here
GOOGLE_API_KEY_2=your-second-api-key-here
GOOGLE_API_KEY_3=your-third-api-key-here

# LLM Configuration
LLM_MODEL_NAME=gemini-2.5-flash-lite
LLM_TEMPERATURE=0.7
LLM_MAX_REQUESTS_PER_KEY=15

# Workflow Configuration
WORKFLOW_MAX_FEEDBACK_LOOPS=3
WORKFLOW_ENABLE_MERMAID=true

# Database Configuration  
NEO4J_PASSWORD=your-neo4j-password
```

## Step-by-Step Migration

### Step 1: Install New Dependencies
```bash
pip install pydantic dependency-injector
```

### Step 2: Test New Architecture
Run the example to make sure everything works:
```bash
python examples/provider_usage.py
```

### Step 3: Migrate One Node at a Time
Start with the translator node:
1. Convert `translator_node` function to `TranslatorNode` class
2. Update the workflow creation to inject the provider
3. Test that specific node

### Step 4: Update Main Application
Modify `src/main.py` to use the new container pattern

### Step 5: Migrate Remaining Nodes
Convert other nodes (junior_editor, fluency_editor, etc.) one by one

### Step 6: Update Tests
Convert tests to use the mock provider instead of patching

## Benefits After Migration

✅ **Automatic Key Rotation**: No more manual key management
✅ **Better Testing**: Easy to inject mock providers
✅ **Environment Configs**: Different settings for dev/prod/test
✅ **Health Monitoring**: Built-in health checks and statistics
✅ **Loose Coupling**: Easy to swap providers or add new ones
✅ **Type Safety**: Full type hints and validation
✅ **Error Recovery**: Automatic retry with different keys

## Troubleshooting

### "No healthy API keys available"
- Check your `.env` file has valid `GOOGLE_API_KEY_*` entries
- Run health check: `await container.health_check()`

### "Import could not be resolved"
- Make sure you installed: `pip install pydantic`
- Check Python path includes `src/` directory

### Tests failing
- Ensure you're using `MockLLMProvider` in test environment
- Set `ENVIRONMENT=testing` in test configuration
