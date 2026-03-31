"""Temporal entity extraction (datetime and duration).

This module provides extraction of temporal expressions including:
- Relative dates (tomorrow, next Monday, december 5th)
- Durations (5 minutes, 2 hours, 3 days)

Requires: ovos-date-parser, ovos-number-parser
"""
from __future__ import annotations

import pathlib
import re
from collections.abc import Generator
from datetime import datetime

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.utils.diff import TextDiff
from simple_NER.utils.log import LOG

try:
    from ovos_date_parser import (
        extract_datetime,
        extract_duration,
        nice_date,
        nice_duration,
    )
    try:
        from ovos_number_parser import numbers_to_digits as _convert_numbers
    except ImportError:
        from ovos_number_parser import convert_words_to_numbers as _convert_numbers  # type: ignore[no-redef]
    _OVOS_AVAILABLE = True
except ImportError:
    _OVOS_AVAILABLE = False
    LOG.warning(
        "ovos-date-parser / ovos-number-parser not installed — "
        "TemporalNER will not function. "
        "Install with: pip install ovos-date-parser ovos-number-parser"
    )
    extract_datetime = None  # type: ignore[assignment]
    extract_duration = None  # type: ignore[assignment]
    nice_date = None  # type: ignore[assignment]
    nice_duration = None  # type: ignore[assignment]
    _convert_numbers = None  # type: ignore[assignment]


_ORDINAL_RE: re.Pattern[str] = re.compile(r'\d+(st|nd|rd|th)\b', re.IGNORECASE)

# Resource directory containing per-language temporal_keywords.txt files.
_RES_DIR = pathlib.Path(__file__).parent.parent / "res"


def _load_temporal_keywords(lang: str) -> frozenset[str]:
    """Load temporal keywords from ``res/<lang>/temporal_keywords.txt``.

    Falls back to ``en-us`` if the requested language file is absent.
    Returns an empty frozenset if neither file exists (rare; degraded mode).

    Args:
        lang: BCP-47 language tag (e.g. ``"de-de"``).

    Returns:
        Frozenset of lowercase keyword strings.
    """
    for candidate in (lang, "en-us"):
        path = _RES_DIR / candidate / "temporal_keywords.txt"
        if path.exists():
            return frozenset(
                line.strip().lower()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")
            )
    return frozenset()


class TemporalNER(BaseAnnotator):
    """Extract datetime and duration entities from text.

    Language support: multi-language via ``ovos-date-parser``. Pass any
    BCP-47 tag supported by that library (e.g. ``"de-de"``, ``"pt-pt"``,
    ``"es-es"``). Defaults to ``"en-us"``.
    Requires ``pip install ovos-date-parser ovos-number-parser``.

    This annotator combines both datetime and duration extraction in a
    single class, as they share common infrastructure (text normalization,
    span tracking).

    Attributes:
        anchor_date: Reference date for relative expressions.
        extract_datetime: Whether to extract datetime entities.
        extract_duration: Whether to extract duration entities.

    Example:
        ```python
        from simple_NER.annotators.temporal_ner import TemporalNER

        ner = TemporalNER()
        for ent in ner.extract_entities("meeting tomorrow at 3pm for 2 hours"):
            print(f"{ent.value} -> {ent.entity_type}")
        ```

    """

    def __init__(
        self,
        anchor_date: datetime | None = None,
        extract_datetime: bool = True,
        extract_duration: bool = True,
        confidence: float = 1.0,
        lang: str = "en-us",
    ) -> None:
        """Initialize temporal NER.

        Args:
            anchor_date: Reference date for relative expressions.
                Defaults to current datetime.
            extract_datetime: Enable datetime extraction.
            extract_duration: Enable duration extraction.
            confidence: Default confidence score for entities.
            lang: BCP-47 language tag forwarded to ovos-date-parser
                (e.g. ``"de-de"``, ``"pt-pt"``, ``"es-es"``).
        """
        self.anchor_date = anchor_date or datetime.now()
        self._extract_datetime = extract_datetime
        self._extract_duration = extract_duration
        super().__init__(confidence=confidence, lang=lang)
        self._temporal_kw: frozenset[str] = _load_temporal_keywords(lang)

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "temporal"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract temporal entities from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for datetime and/or duration expressions.
        """
        if not _OVOS_AVAILABLE:
            return

        if self._extract_datetime:
            yield from self._extract_datetime_entities(text)
        if self._extract_duration:
            yield from self._extract_duration_entities(text)

    def _extract_datetime_entities(
        self, text: str
    ) -> Generator[Entity, None, None]:
        """Extract datetime entities from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for datetime expressions.
        """
        if extract_datetime is None:
            return

        # Convert written numbers to digits for better parsing
        conv = _convert_numbers(text, self.lang) if _convert_numbers else text
        if conv != text:
            LOG.debug(f"Text normalized: '{text}' -> '{conv}'")

        dt_result = extract_datetime(conv, self.lang, self.anchor_date)
        if dt_result:
            date, remainder = dt_result
            diff = TextDiff(conv, remainder)

            for _tag, span1, _span2 in diff.dif_tags():
                value = " ".join(conv.split()[span1[0] : span1[1]])

                # Skip spans that are stopwords + bare number — ovos-date-parser
                # interprets digits as times (e.g. "500" → 5:00 AM), causing
                # false positives when currency amounts are number-normalised.
                # A real temporal span contains at least one temporal keyword
                # (month name, weekday, relative word) or an ordinal suffix.
                value_lower = value.lower()
                has_temporal = (
                    any(kw in value_lower.split() for kw in self._temporal_kw)
                    or _ORDINAL_RE.search(value)
                )
                if not has_temporal:
                    continue

                # Re-extract to get accurate date for this specific value
                date_result = extract_datetime(value, self.lang, self.anchor_date)
                if date_result:
                    date = date_result[0]
                    data = {
                        "timestamp": date.timestamp(),
                        "isoformat": date.isoformat(),
                        "weekday": date.isoweekday(),
                        "month": date.month,
                        "day": date.day,
                        "hour": date.hour,
                        "minute": date.minute,
                        "year": date.year,
                        "spoken": nice_date(date, self.lang, now=self.anchor_date) if nice_date else "",
                    }
                    yield Entity(
                        value,
                        "relative_date",
                        source_text=text,
                        confidence=self.confidence,
                        data=data,
                    )

    def _extract_duration_entities(
        self, text: str
    ) -> Generator[Entity, None, None]:
        """Extract duration entities from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for duration expressions.
        """
        if extract_duration is None:
            return

        # Convert written numbers to digits for better parsing
        conv = _convert_numbers(text, self.lang) if _convert_numbers else text
        if conv != text:
            LOG.debug(f"Text normalized: '{text}' -> '{conv}'")

        delta, remainder = extract_duration(text, self.lang)
        if delta:
            diff = TextDiff(conv, remainder)

            for _tag, span1, _span2 in diff.dif_tags():
                value = " ".join(conv.split()[span1[0] : span1[1]])

                # Skip spans that contain no temporal keyword — mirrors the
                # guard in _extract_datetime_entities to prevent bare numbers
                # (e.g. "$500" normalised to "500") matching as durations.
                # Substring check (not exact-word) handles plural forms:
                # "minutes" contains keyword "minute", "hours" contains "hour".
                value_lower = value.lower()
                has_temporal = any(
                    kw in word
                    for word in value_lower.split()
                    for kw in self._temporal_kw
                )
                if not has_temporal:
                    continue

                # Re-extract to get accurate duration for this specific value
                delta_result, _ = extract_duration(value, self.lang)
                if delta_result:
                    data = {
                        "days": delta_result.days,
                        "seconds": delta_result.seconds,
                        "microseconds": delta_result.microseconds,
                        "total_seconds": delta_result.total_seconds(),
                        "spoken": nice_duration(delta_result.total_seconds(), self.lang).strip() if nice_duration else "",
                    }
                    yield Entity(
                        value,
                        "duration",
                        source_text=text,
                        confidence=self.confidence,
                        data=data,
                    )


# Backward compatibility aliases
DateTimeNER = TemporalNER
TimedeltaNER = TemporalNER


if __name__ == "__main__":
    from pprint import pprint

    if not _OVOS_AVAILABLE:
        print("ERROR: Install ovos-date-parser and ovos-number-parser")
        print("pip install ovos-date-parser ovos-number-parser")
    else:
        print("=" * 60)
        print("DATETIME EXTRACTION")
        print("=" * 60)

        ner = TemporalNER()
        for r in ner.extract_entities(
            "tomorrow is X yesterday was Y in 10 days it will be Z"
        ):
            pprint(r.as_json())

        print("\n" + "=" * 60)
        print("DURATION EXTRACTION")
        print("=" * 60)

        for r in ner.extract_entities(
            "5 minutes ago was X 10 minutes from now is Y in 19 hours will be N"
        ):
            pprint(r.as_json())
