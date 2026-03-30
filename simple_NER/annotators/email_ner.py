"""Email entity extraction using regex patterns."""
from __future__ import annotations

import re
from collections.abc import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.rules.rx import RegexNER


class EmailNER(RegexNER):
    """Extract email addresses from text using regex patterns.

    Language support: language-agnostic (RFC 5321 regex).

    Example:
        ```python
        from simple_NER.annotators.email_ner import EmailNER

        ner = EmailNER()
        for ent in ner.extract_entities("contact test@example.com"):
            print(f"{ent.value} -> {ent.entity_type}")
        ```
    """

    EMAIL_REGEX = (
        r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|'
        r'"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|'
        r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@'
        r'(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9]'
        r'(?:[a-z0-9-]*[a-z0-9])?|'
        r'\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|'
        r'[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|'
        r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
    )

    def __init__(self) -> None:
        """Initialize EmailNER with email regex pattern."""
        super().__init__()
        self.add_rule("email", self.EMAIL_REGEX)

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "email"


# Also provide a BaseAnnotator version for consistency
class EmailAnnotator(BaseAnnotator):
    """Alternative email extractor using BaseAnnotator pattern."""

    EMAIL_REGEX = EmailNER.EMAIL_REGEX

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "email"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract email addresses from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for email addresses found.
        """
        for match in re.finditer(self.EMAIL_REGEX, text, re.IGNORECASE):
            yield Entity(
                match.group(),
                "email",
                source_text=text,
                confidence=self.confidence,
            )
