"""Written number entity extraction.

This module provides extraction of written numbers from text
(e.g., "three hundred" -> 300) with numtag.
"""
from __future__ import annotations

from collections.abc import Generator

from numtag import Form, Kind, Scale, tag_numbers
from numtag.tagger import ARTICLE_CONFIDENCE

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.utils.log import LOG


class NumberNER(BaseAnnotator):
    """Extract written numbers from text.

    Language support: every language numtag has a lexicon for. Pass a
    BCP-47 tag (e.g. ``"de-de"``, ``"pt-pt"``, ``"es-es"``). Defaults to
    ``"en-us"``.

    This annotator finds written numbers (e.g., "three hundred", "fifth")
    and extracts each one as an entity with its canonical digit string.
    Numbers written only in digits are not written numbers, and a lone
    article ("uma casa") is no number.

    Attributes:
        ordinals: Whether to extract ordinal numbers (1st, 2nd, third).
        short_scale: Use short scale for large numbers (US) vs long scale (UK).
        case_sensitive: Whether to match case-sensitively.

    Example:
        ```python
        from simple_NER.annotators.numbers_ner import NumberNER

        ner = NumberNER()
        for ent in ner.extract_entities("I have three hundred apples"):
            print(f"{ent.value} -> {ent.data['number']}")
            # "three hundred" -> 300
        ```

    """

    def __init__(
        self,
        ordinals: bool = True,
        short_scale: bool = True,
        case_sensitive: bool = False,
        confidence: float = 1.0,
        lang: str = "en-us",
    ) -> None:
        """Initialize NumberNER.

        Args:
            ordinals: Whether to extract ordinal numbers.
            short_scale: Use short scale for large numbers.
            case_sensitive: Whether to match case-sensitively.
            confidence: Default confidence score for entities.
            lang: BCP-47 language tag forwarded to numtag
                (e.g. ``"de-de"``, ``"pt-pt"``, ``"es-es"``).
        """
        super().__init__(confidence=confidence, lang=lang)
        self.ordinals = ordinals
        self.short_scale = short_scale
        self._case_sensitive = case_sensitive

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "numbers"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract written numbers from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for detected written numbers.
        """
        # Normalize case if not case-sensitive
        original_text = text
        if not self._case_sensitive:
            text = text.lower()

        scale = Scale.SHORT if self.short_scale else Scale.LONG
        try:
            mentions = tag_numbers(text, self.lang, scale=scale)
        except Exception as e:
            LOG.error(f"Error extracting written numbers: {e}")
            return

        for mention in mentions:
            if mention.form is Form.DIGITS or mention.confidence <= ARTICLE_CONFIDENCE:
                continue
            if mention.kind is Kind.ORDINAL and not self.ordinals:
                continue
            start, end = mention.char_span
            yield Entity(
                mention.text,
                "written_number",
                source_text=original_text,
                confidence=self.confidence,
                data={"number": mention.value, "start": start, "end": end},
            )


if __name__ == "__main__":
    from pprint import pprint

    print("=" * 60)
    print("WRITTEN NUMBER EXTRACTION")
    print("=" * 60)

    ner = NumberNER()
    text = "three hundred trillion tons of spinning metal"

    print(f"\nText: {text}")
    print("-" * 60)

    for r in ner.extract_entities(text):
        pprint(r.as_json())

    print("\n" + "=" * 60)
    print("WITH ORDINALS")
    print("=" * 60)

    text2 = "the 5th number of the third thing"
    print(f"\nText: {text2}")
    print("-" * 60)

    for r in ner.extract_entities(text2):
        pprint(r.as_json())
