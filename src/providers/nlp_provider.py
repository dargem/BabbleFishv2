"""NLP Provider for managing spaCy models efficiently."""

import threading
import logging
from typing import Dict
import spacy
import spacy.cli
from src.core import LanguageType
from spacy.language import Language
from typing import List

logger = logging.getLogger(__name__)


class NLPProvider:
    """
    Proviedes text preprocessing services
    Lazy loads models when needed
    """

    def __init__(self):
        self._models: Dict[LanguageType, Language] = {}
        logger.debug("NLPProvider initialized")

        self._LANGUAGE_CODE_MAP = {
            LanguageType.ENGLISH: "en",
            LanguageType.CHINESE: "zh",
            LanguageType.JAPANESE: "ja",
            LanguageType.KOREAN: "ko",
            LanguageType.SPANISH: "es",
            LanguageType.FRENCH: "fr",
        }

    def _load_model(self, language: LanguageType):
        """
        Called when the NLP Provider doesn't have a model for the needed language

        Args:
            language: Language enum that the provider needs a model for
        """

        # options are sm, md, lg and trf, some trf are missing dep on lang
        logging.info("Loading spacy model for lang %s", language)
        model = "%s_core_web_%s" % (self._LANGUAGE_CODE_MAP[language], "sm")

        try:
            nlp = spacy.load(model)
            logging.info("Spacy model for lang %s loaded", language)
        except OSError:
            logging.warning("Model %s not found, attempting to download...", model)
            try:
                # Download the model using spacy's download function
                spacy.cli.download(model)
                nlp = spacy.load(model)
                logging.info("Successfully downloaded and loaded model %s", model)
            except Exception as e:
                logging.error("Failed to download model %s: %s", model, str(e))
                raise RuntimeError(
                    f"Could not load or download spaCy model '{model}' for language {language}"
                )

        self._models[language] = nlp

    def _get_model(self, language: LanguageType) -> Language:
        """
        Helper method returns needed spacy model, loads a model if needed

        Args:
            language: The language of the text to be processed

        Returns:
            Spacy language processor
        """
        if language not in self._models:
            self._load_model(language)
        return self._models[language]

    def extract_lemma_nouns(
        self, text_list: List[str], language: LanguageType
    ) -> List[str]:
        """
        Lemmatises and extracts nouns from inputted list of str

        Args:
            text_list: List of strings for processing
            language: LanguageType enum to determine language for needed model

        Returns:
            List of only nouns from input strings
        """
        nlp = self._get_model(language)
        return [self._extract_nouns_from_text(text, nlp) for text in text_list]

    def _extract_nouns_from_text(self, text: str, nlp: Language) -> str:
        """
        Helper method for extract lemma nouns, doing it on a chapter based process

        Args:
            text: A string of text for processing
            nlp: Appropriate spacy model
        Returns:
            List of only nouns from input strings
        """

        # Process text with spaCy
        doc = nlp(text)
        lemmatisation = True
        pos_tagging = True
        # Validate this spacy model has POS tagging + lemmatisation
        if "tagger" not in nlp.pipe_names:
            logging.error(
                "NLP pipeline %s doesn't have POS tagger, major error skipping tagging",
                nlp.meta["name"],
            )
            pos_tagging = False
        if "lemmatizer" not in nlp.pipe_names:
            logging.warning(
                "NLP pipeline %s doesn't have lemmatiser, skipping lemmatisation",
                nlp.meta["name"],
            )
            lemmatisation = False

        # Extract nouns (NOUN and PROPN tags)
        nouns = []
        for token in doc:
            if not (
                pos_tagging
                and token.pos_ in ["NOUN", "PROPN"]  # Only nouns and proper nouns
                and not token.is_stop  # Skip stop words
                and not token.is_punct  # Skip punctuation
                and not token.is_space  # Skip whitespace
                and token.is_alpha  # Only alphabetic characters
            ):
                continue  # early stopping

            # Use lemma to normalize plurals etc.
            if lemmatisation:
                nouns.append(token.lemma_.lower())
                continue  # early stopping

            # Just append if no lemmatisation done
            nouns.append(token.text)

        return " ".join(nouns)
