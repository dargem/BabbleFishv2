"""NLP Provider for managing spaCy models efficiently."""

import threading
import logging
from typing import Dict, Any
import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)


class NLPProvider:
    """Thread-safe provider for spaCy NLP models.
    
    Manages spaCy model lifecycle efficiently by:
    - Loading models once and reusing them
    - Thread-safe access to shared models
    - Lazy loading of models only when needed
    """
    
    def __init__(self):
        self._models: Dict[str, Language] = {}
        self._lock = threading.Lock()
        logger.debug("NLPProvider initialized")
    
    def get_model(self, model_name: str = "en_core_web_sm") -> Language:
        """Get a spaCy model, loading it if necessary.
        
        Args:
            model_name: Name of the spaCy model to load
            
        Returns:
            Loaded spaCy Language model
            
        Raises:
            OSError: If the model cannot be loaded
        """
        if model_name not in self._models:
            with self._lock:
                # Double-check pattern to avoid race conditions
                if model_name not in self._models:
                    logger.info(f"Loading spaCy model: {model_name}")
                    try:
                        self._models[model_name] = spacy.load(model_name)
                        logger.debug(f"Successfully loaded spaCy model: {model_name}")
                    except OSError as e:
                        logger.error(f"Failed to load spaCy model {model_name}: {e}")
                        raise
        
        return self._models[model_name]
    
    def is_model_loaded(self, model_name: str = "en_core_web_sm") -> bool:
        """Check if a model is already loaded.
        
        Args:
            model_name: Name of the spaCy model
            
        Returns:
            True if model is loaded, False otherwise
        """
        return model_name in self._models
    
    def get_loaded_models(self) -> list[str]:
        """Get list of currently loaded model names.
        
        Returns:
            List of loaded model names
        """
        return list(self._models.keys())
    
    def clear_models(self) -> None:
        """Clear all loaded models from memory.
        
        Useful for memory management in long-running applications.
        """
        with self._lock:
            logger.info(f"Clearing {len(self._models)} loaded spaCy models")
            self._models.clear()


class ThreadLocalNLPProvider:
    """Thread-local NLP provider for maximum isolation.
    
    Each thread gets its own copy of the spaCy model.
    Use this if you need guaranteed thread isolation or if
    you're modifying pipeline components at runtime.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name = model_name
        self._local = threading.local()
        logger.debug(f"ThreadLocalNLPProvider initialized for model: {model_name}")
    
    @property
    def nlp(self) -> Language:
        """Get thread-local spaCy model."""
        if not hasattr(self._local, 'nlp'):
            logger.debug(f"Loading thread-local spaCy model: {self.model_name}")
            self._local.nlp = spacy.load(self.model_name)
        return self._local.nlp