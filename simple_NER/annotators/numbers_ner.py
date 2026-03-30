"""Written number entity extraction.

This module provides extraction of written numbers from text
(e.g., "three hundred" -> 300).

Requires: ovos-number-parser
"""
from __future__ import annotations

from collections.abc import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.utils.diff import TextDiff
from simple_NER.utils.log import LOG

try:
    from ovos_number_parser import convert_words_to_numbers as _convert_numbers
    _OVOS_AVAILABLE = True
except ImportError:
    _OVOS_AVAILABLE = False
    LOG.warning(
        "ovos-number-parser not installed — NumberNER will not function. "
        "Install with: pip install ovos-number-parser"
    )
    _convert_numbers = None  # type: ignore[assignment]


class NumberNER(BaseAnnotator):
    """Extract written numbers from text.

    Language support: multi-language via ``ovos-number-parser``. Pass any
    BCP-47 tag supported by that library (e.g. ``"de-de"``, ``"pt-pt"``,
    ``"es-es"``). Defaults to ``"en-us"``.
    Requires ``pip install ovos-number-parser``.

    This annotator converts written numbers (e.g., "three hundred", "fifth")
    to their numeric equivalents and extracts them as entities.

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
            # "three hundred" -> 300.0
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
            lang: BCP-47 language tag forwarded to ovos-number-parser
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
        if _convert_numbers is None:
            return

        # Normalize case if not case-sensitive
        original_text = text
        if not self._case_sensitive:
            text = text.lower()
            if text.lower() != original_text.lower():
                LOG.debug(f"Text normalized: '{original_text}' -> '{text}'")

        try:
            # Convert written numbers to digits
            if self.ordinals:
                replaced = _convert_numbers(
                    text,
                    short_scale=self.short_scale,
                    ordinals=True,
                    lang=self.lang,
                )
            else:
                replaced = _convert_numbers(
                    text,
                    short_scale=self.short_scale,
                    ordinals=False,
                    lang=self.lang,
                )

            # Find differences to locate written numbers
            diff = TextDiff(text, replaced)
            for _tag, span1, span2 in diff.dif_tags():
                value = " ".join(text.split()[span1[0] : span1[1]])
                numeric = " ".join(replaced.split()[span2[0] : span2[1]])

                data = {"number": numeric}
                yield Entity(
                    value,
                    "written_number",
                    source_text=original_text,
                    confidence=self.confidence,
                    data=data,
                )
        except Exception as e:
            LOG.error(f"Error extracting written numbers: {e}")


if __name__ == "__main__":
    from pprint import pprint

    if not _OVOS_AVAILABLE:
        print("ERROR: Install ovos-number-parser")
    else:
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
