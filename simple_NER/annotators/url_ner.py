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

    Language support: language-agnostic. Supports internationalized domain
    names (IDN) with Unicode characters (e.g. ``https://münchen.de``).

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

    # URL label character: ASCII alnum + Unicode letters/digits (IDN support)
    _LABEL_CHAR = r'[A-Za-z0-9\u00C0-\u024F\u0400-\u04FF\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]'
    _LABEL = rf'{_LABEL_CHAR}(?:[{_LABEL_CHAR[1:-1]}\-]{{0,61}}{_LABEL_CHAR})?'

    URL_PATTERN = re.compile(
        r'https?://'                                         # scheme
        r'(?:'
        rf'(?:{_LABEL}\.)+{_LABEL}'                          # hostname (including IDN)
        r'|localhost'                                        # localhost
        r'|\d{1,3}(?:\.\d{1,3}){3}'                         # IPv4
        r')'
        r'(?::\d{1,5})?'                                     # optional port
        r'(?:/[^\s]*)?',                                     # optional path/query
        re.IGNORECASE | re.UNICODE,
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
