"""Phone number entity extraction.

This module provides extraction of phone numbers from text.
"""
from __future__ import annotations

import re
from typing import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator


class PhoneAnnotator(BaseAnnotator):
    """Extract phone numbers from text.

    Language support: language-agnostic (regex on digit/punctuation patterns).
    Covers international (+E.164), US, and simple local formats.

    This annotator identifies phone numbers in various formats:
    - International: +1-555-123-4567, +44 20 7946 0958
    - US: (555) 123-4567, 555-123-4567, 555.123.4567
    - Simple: 123-4567, 123.4567

    Example:
        ```python
        from simple_NER.annotators.phone_ner import PhoneAnnotator

        ner = PhoneAnnotator()
        text = "Call +1-555-123-4567 or (555) 987-6543"
        for ent in ner.extract_entities(text):
            print(f"{ent.value} -> {ent.entity_type}")
        ```
    """

    # Extension suffix pattern (x123, ext 456, ext. 789)
    _EXT = r'(?:\s*(?:x|ext\.?)\s*\d{1,5})?'

    PHONE_PATTERN = re.compile(
        r'(?:'
        r'(?:\+\d{1,3}[-.\s]?)?'  # Optional country code
        r'(?:\(?\d{3}\)?[-.\s]?)'  # Area code
        r'\d{3}[-.\s]?\d{4}'       # Main number
        + _EXT +
        r')'
        r'|'
        r'(?:\d{3}[-.\s]?\d{4})'   # Simple local number
        + _EXT,
    )

    def __init__(
        self,
        confidence: float = 0.85,
        min_length: int = 7,
        require_country_code: bool = False,
    ) -> None:
        """Initialize PhoneAnnotator.

        Args:
            confidence: Default confidence score.
            min_length: Minimum digits required.
            require_country_code: Only match numbers with country code.
        """
        super().__init__(confidence=confidence)
        self._min_length = min_length
        self._require_country_code = require_country_code

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "phone"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract phone numbers from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for detected phone numbers.
        """
        for match in self.PHONE_PATTERN.finditer(text):
            phone = match.group()

            # Count digits
            digits = re.sub(r'\D', '', phone)

            # Skip if too short
            if len(digits) < self._min_length:
                continue

            # Skip if requires country code but doesn't have one
            if self._require_country_code and not phone.startswith('+'):
                continue

            # Determine type based on format
            phone_type = self._classify_phone(phone, digits)

            yield Entity(
                value=phone,
                entity_type="phone_number",
                source_text=text,
                confidence=self.confidence,
                data={
                    "digits": digits,
                    "digit_count": len(digits),
                    "type": phone_type,
                    "has_country_code": phone.startswith('+'),
                    "start": match.start(),
                    "end": match.end(),
                }
            )

    def _classify_phone(self, phone: str, digits: str) -> str:
        """Classify phone number type.

        Args:
            phone: Original phone string.
            digits: Digits only.

        Returns:
            Phone type classification.
        """
        if phone.startswith('+'):
            return "international"
        elif len(digits) == 10:
            return "us_national"
        elif len(digits) == 7:
            return "local"
        else:
            return "other"


if __name__ == "__main__":
    ner = PhoneAnnotator()
    text = """
    Call us at +1-555-123-4567 or (555) 987-6543.
    UK office: +44 20 7946 0958
    Local: 555.123.4567 or just 123-4567
    """

    print(f"Text: {text.strip()}")
    print("-" * 60)

    for ent in ner.extract_entities(text):
        print(f"{ent.value:20} -> {ent.entity_type} ({ent.data['type']})")
