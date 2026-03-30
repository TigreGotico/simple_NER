"""Hashtag entity extraction.

This module provides extraction of hashtags from text.
"""
from __future__ import annotations

import re
from typing import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator


class HashtagAnnotator(BaseAnnotator):
    """Extract hashtags from text.

    Language support: language-agnostic. Unicode flag enabled so non-Latin
    scripts work automatically: ``#هاشتاق``, ``#タグ``, ``#标签``, ``#тег``.

    This annotator identifies hashtags commonly used in social media:
    - Standard: #hashtag, #HashTag
    - With numbers: #tag123
    - Multiple words: #ThisIsATag
    - Non-Latin: #هاشتاق, #タグ, #标签

    Example:
        ```python
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator

        ner = HashtagAnnotator()
        text = "Love this! #awesome #BestDayEver #2024"
        for ent in ner.extract_entities(text):
            print(f"{ent.value} -> {ent.entity_type}")
        ```
    """

    # Hashtag pattern — re.UNICODE enables non-Latin scripts automatically.
    # \w matches [A-Za-z0-9_] plus Unicode letters/digits (Arabic, CJK, etc.)
    HASHTAG_PATTERN = re.compile(
        r'#(?!\d+(?:\W|$))'  # Must not be all digits
        r'\w{2,50}'           # 2-50 word characters (Unicode)
        r'(?!\w)',            # Word boundary
        re.UNICODE,
    )

    def __init__(
        self,
        confidence: float = 0.9,
        min_length: int = 2,
        max_length: int = 50,
    ) -> None:
        """Initialize HashtagAnnotator.

        Args:
            confidence: Default confidence score.
            min_length: Minimum hashtag length (excluding #).
            max_length: Maximum hashtag length.
        """
        super().__init__(confidence=confidence)
        self._min_length = min_length
        self._max_length = max_length

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "hashtag"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract hashtags from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for detected hashtags.
        """
        for match in self.HASHTAG_PATTERN.finditer(text):
            hashtag = match.group()
            tag_text = hashtag[1:]  # Remove #

            # Skip if too short or too long
            if len(tag_text) < self._min_length or len(tag_text) > self._max_length:
                continue

            # Skip if all numbers
            if tag_text.isdigit():
                continue

            # Classify hashtag type
            tag_type = self._classify_hashtag(tag_text)

            yield Entity(
                value=hashtag,
                entity_type="hashtag",
                source_text=text,
                confidence=self.confidence,
                data={
                    "tag": tag_text,
                    "type": tag_type,
                    "length": len(tag_text),
                    "start": match.start(),
                    "end": match.end(),
                }
            )

    def _classify_hashtag(self, tag: str) -> str:
        """Classify hashtag type.

        Args:
            tag: Hashtag text (without #).

        Returns:
            Hashtag type classification.
        """
        if tag.isupper():
            return "shouting"
        elif tag.islower():
            return "lowercase"
        elif tag[0].isupper() and any(c.isupper() for c in tag[1:]):
            return "CamelCase"
        elif '_' in tag:
            return "underscored"
        elif any(c.isdigit() for c in tag):
            return "alphanumeric"
        else:
            return "mixed"


if __name__ == "__main__":
    ner = HashtagAnnotator()
    text = """
    Great day! #awesome #BestDayEver #summer2024
    Check out #Machine_Learning and #AI trends.
    #TOO_LONG_HASHTAG_THAT_EXCEEDS_FIFTY_CHARACTERS_LIMIT
    #123 (should be skipped - numbers only)
    #ok (should be included)
    """

    print(f"Text: {text.strip()}")
    print("-" * 60)

    for ent in ner.extract_entities(text):
        data = ent.data
        print(f"{ent.value:25} -> {data['type']} (len: {data['length']})")
