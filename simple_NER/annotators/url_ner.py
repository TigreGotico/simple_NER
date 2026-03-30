"""URL entity extraction.

This module provides extraction of URLs from text.
"""
from __future__ import annotations

import re
from typing import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator


class URLAnnotator(BaseAnnotator):
    """Extract URLs from text.

    Language support: language-agnostic (regex on URL syntax).

    This annotator identifies HTTP/HTTPS URLs using regex patterns.

    Example:
        ```python
        from simple_NER.annotators.url_ner import URLAnnotator

        ner = URLAnnotator()
        text = "Visit https://example.com or http://test.org/page"
        for ent in ner.extract_entities(text):
            print(f"{ent.value} -> {ent.entity_type}")
        ```
    """

    # Comprehensive URL pattern
    URL_PATTERN = re.compile(
        r'https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain
        r'[A-Z]{2,6}\.?|'
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP address
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)?',  # path
        re.IGNORECASE
    )

    def __init__(self, confidence: float = 0.95) -> None:
        """Initialize URLAnnotator.

        Args:
            confidence: Default confidence score for extracted URLs.
        """
        super().__init__(confidence=confidence)

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "url"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract URLs from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for detected URLs.
        """
        for match in self.URL_PATTERN.finditer(text):
            url = match.group()
            yield Entity(
                value=url,
                entity_type="url",
                source_text=text,
                confidence=self.confidence,
                data={
                    "protocol": "https" if url.startswith("https") else "http",
                    "start": match.start(),
                    "end": match.end(),
                }
            )


if __name__ == "__main__":
    ner = URLAnnotator()
    text = "Visit https://example.com or http://test.org/page?q=1"

    print(f"Text: {text}")
    print("-" * 60)

    for ent in ner.extract_entities(text):
        print(f"{ent.value} -> {ent.entity_type} (conf: {ent.confidence:.2f})")
