"""Name entity extraction using regex patterns.

This module provides extraction of proper nouns (names) from text
using regex patterns.
"""
from __future__ import annotations

import re
from collections.abc import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator


class NamesNER(BaseAnnotator):
    """Extract proper nouns (names) from text using regex patterns.

    Language support: English only (relies on Latin capitalisation convention).

    This annotator uses a regex pattern to identify capitalized words
    that are likely to be proper nouns (names of people, organizations, etc.).

    Attributes:
        confidence_threshold: Minimum confidence score for entities.
        min_word_length: Minimum length of words to consider.

    Example:
        ```python
        from simple_NER.annotators.names_ner import NamesNER

        ner = NamesNER()
        for ent in ner.extract_entities("John Doe met Alice Smith"):
            print(f"{ent.value} -> {ent.entity_type} (confidence: {ent.confidence})")
        ```
    """

    # Regex pattern for matching proper nouns
    NAMES_PATTERN = re.compile(
        r"\b((?:[A-Z][a-z][-A-Za-z']*(?: *[A-Z][a-z][-A-Za-z']*)*)\b|"
        r"\b(?:[A-Z][a-z][-A-Za-z']*))\b"
    )

    def __init__(
        self,
        confidence_threshold: float = 0.65,
        min_word_length: int = 2,
        confidence: float | None = None,
    ) -> None:
        """Initialize NamesNER.

        Args:
            confidence_threshold: Minimum confidence score for detected names.
            min_word_length: Minimum length of words to consider as names.
            confidence: Alias for confidence_threshold (for factory compatibility).
        """
        # Support both parameter names for factory compatibility
        final_confidence = confidence if confidence is not None else confidence_threshold
        super().__init__(confidence=final_confidence)
        self._min_word_length = min_word_length

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "names"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract proper nouns from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for detected proper nouns.
        """
        for match in self.NAMES_PATTERN.finditer(text):
            word = match.group()

            # Skip words that are too short
            if len(word) < self._min_word_length:
                continue

            # Calculate confidence based on capitalization pattern
            if word[0].isupper():
                confidence = 0.8
            else:
                confidence = 0.65

            # Skip if below threshold
            if confidence < self.confidence:
                continue

            yield Entity(
                word,
                "Noun",
                source_text=text,
                confidence=confidence,
                data={"pattern": "proper_noun"},
            )


if __name__ == "__main__":
    from pprint import pprint

    ner = NamesNER()
    text = "I am JarbasAI, but my real name is Casimiro"

    print(f"Processing: {text}")
    print("-" * 60)

    for e in ner.extract_entities(text):
        pprint(e.as_json())
