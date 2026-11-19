"""Temporal entity extraction (datetime and duration).

This module provides extraction of temporal expressions including:
- Relative dates (tomorrow, next Monday, december 5th)
- Durations (5 minutes, 2 hours, 3 days)

Requires: chronologia, ovos-date-parser (for the spoken forms)
"""
from __future__ import annotations

import pathlib
import re
from collections.abc import Generator
from datetime import datetime

from chronologia import extract_duration, extract_timespan
from ovos_date_parser import nice_date, nice_duration

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.utils.diff import TextDiff
from simple_NER.utils.log import LOG

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
    lang = lang.lower().split("-")[0]
    for candidate in (lang, "en"):
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

    Language support: every language chronologia has a locale for. Pass a
    BCP-47 tag (e.g. ``"de-de"``, ``"pt-pt"``, ``"es-es"``). Defaults to
    ``"en-us"``.

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
            lang: BCP-47 language tag forwarded to chronologia
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
        try:
            if self._extract_datetime:
                yield from self._extract_datetime_entities(text)
            if self._extract_duration:
                yield from self._extract_duration_entities(text)
        except NotImplementedError as e:
            LOG.error(f"Error extracting dates and durations: {e}")

    def _extract_datetime_entities(
        self, text: str
    ) -> Generator[Entity, None, None]:
        """Extract datetime entities from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for datetime expressions.
        """
        found = extract_timespan(text, self.lang, self.anchor_date)
        if found:
            diff = TextDiff(text, found.remainder)

            for _tag, span1, _span2 in diff.dif_tags():
                value = " ".join(text.split()[span1[0] : span1[1]])

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
                span_result = extract_timespan(value, self.lang, self.anchor_date)
                if span_result and span_result.span.start_datetime:
                    date = span_result.span.start_datetime
                    data = {
                        "timestamp": date.timestamp(),
                        "isoformat": date.isoformat(),
                        "weekday": date.isoweekday(),
                        "month": date.month,
                        "day": date.day,
                        "hour": date.hour,
                        "minute": date.minute,
                        "year": date.year,
                        "spoken": nice_date(date, self.lang, now=self.anchor_date),
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
        found = extract_duration(text, self.lang, self.anchor_date)
        if found:
            diff = TextDiff(text, found.remainder)

            for _tag, span1, _span2 in diff.dif_tags():
                value = " ".join(text.split()[span1[0] : span1[1]])

                # Skip spans that contain no temporal keyword.
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
                duration_result = extract_duration(value, self.lang, self.anchor_date)
                if duration_result:
                    delta_result = duration_result.duration
                    data = {
                        "days": delta_result.days,
                        "seconds": delta_result.seconds,
                        "microseconds": delta_result.microseconds,
                        "total_seconds": delta_result.total_seconds(),
                        "spoken": nice_duration(delta_result.total_seconds(), self.lang).strip(),
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
