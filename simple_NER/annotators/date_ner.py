"""Explicit date entity extraction.

This module provides extraction of explicit dates from text.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator


class DateAnnotator(BaseAnnotator):
    """Extract explicit dates from text.

    Language support: numeric formats (ISO, MM/DD/YYYY, DD/MM/YYYY) are
    language-agnostic. Written month names are recognised in English, Spanish,
    French, German, Portuguese, Italian, and Dutch.

    This annotator identifies dates in various formats:
    - US: MM/DD/YYYY, MM-DD-YYYY
    - EU: DD/MM/YYYY, DD-MM-YYYY
    - ISO: YYYY-MM-DD
    - Written: January 5, 2024 / 5 January 2024
    - Short: Jan 5, 2024 / 5 Jan 2024

    Example:
        ```python
        from simple_NER.annotators.date_ner import DateAnnotator

        ner = DateAnnotator()
        text = "Meeting on 12/25/2024 and Jan 5, 2025"
        for ent in ner.extract_entities(text):
            print(f"{ent.value} -> {ent.entity_type}")
        ```
    """

    # Month names and abbreviations — English, Spanish, French, German,
    # Portuguese, Italian, Dutch
    MONTHS = {
        # English
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12,
        # Spanish
        'enero': 1, 'ene': 1,
        'febrero': 2,
        'marzo': 3,
        'abril': 4,
        'mayo': 5,
        'junio': 6,
        'julio': 7,
        'agosto': 8,
        'septiembre': 9, 'set': 9,
        'octubre': 10,
        'noviembre': 11,
        'diciembre': 12,
        # French
        'janvier': 1,
        'février': 2, 'fevrier': 2,
        'mars': 3,
        'avril': 4,
        'mai': 5,
        'juin': 6,
        'juillet': 7,
        'août': 8, 'aout': 8,
        'septembre': 9,
        'octobre': 10,
        'novembre': 11,
        'décembre': 12, 'decembre': 12,
        # German
        'januar': 1, 'jän': 1, 'jaen': 1,
        'februar': 2,
        # 'märz' handled below via 'marz'
        'märz': 3, 'marz': 3,
        # april same as English
        # mai same as French
        # juni / juli
        'juni': 6,
        'juli': 7,
        # august same as English
        # september already covered
        'oktober': 10,
        # november already covered
        'dezember': 12,
        # Portuguese
        'janeiro': 1,
        'fevereiro': 2,
        'março': 3, 'marco': 3,
        # abril same as Spanish
        # maio / junho / julho
        'maio': 5,
        'junho': 6,
        'julho': 7,
        # agosto same as Spanish
        # setembro / outubro / novembro / dezembro
        'setembro': 9,
        'outubro': 10,
        'novembro': 11,
        'dezembro': 12,
        # Italian
        'gennaio': 1,
        'febbraio': 2,
        'marzo': 3,
        # aprile
        'aprile': 4,
        'maggio': 5,
        'giugno': 6,
        'luglio': 7,
        # agosto same as Spanish
        'settembre': 9,
        # ottobre / novembre / dicembre
        'ottobre': 10,
        # novembre same as English
        'dicembre': 12,
        # Dutch
        'januari': 1,
        'februari': 2,
        # maart
        'maart': 3,
        # april same
        # mei
        'mei': 5,
        # juni / juli same as German
        # augustus
        'augustus': 8,
        # september same
        # oktober
        'oktober': 10,
        # november same
        # december
        'december': 12,
    }

    # All recognised month tokens (built from MONTHS dict at class definition time).
    # Using a property would require an instance; a classmethod is cleaner.
    @classmethod
    def _month_pattern(cls) -> str:
        """Return a regex alternation of all known month tokens, longest first."""
        tokens = sorted(cls.MONTHS.keys(), key=len, reverse=True)
        return '|'.join(re.escape(t) for t in tokens)

    # Date patterns — month token is substituted at compile time in __init__.
    # Literal braces for regex quantifiers are doubled so str.format() ignores them.
    _DATE_PATTERN_TEMPLATES = [
        # ISO: YYYY-MM-DD
        (r'\b(\d{{4}})-(\d{{1,2}})-(\d{{1,2}})\b', 'ISO'),
        # Numeric: MM/DD/YYYY or MM-DD-YYYY or DD/MM/YYYY
        (r'\b(\d{{1,2}})[/\-](\d{{1,2}})[/\-](\d{{4}})\b', 'US'),
        # Written: Month DD, YYYY  (en/es/fr/de/pt/it/nl)
        (r'\b({months})\s+(\d{{1,2}}),?\s+(\d{{4}})\b', 'WRITTEN_US'),
        # Written: DD Month YYYY
        (r'\b(\d{{1,2}})\s+({months})\s+(\d{{4}})\b', 'WRITTEN_EU'),
    ]

    def __init__(
        self,
        confidence: float = 0.9,
        prefer_us_format: bool = True,
    ) -> None:
        """Initialize DateAnnotator.

        Args:
            confidence: Default confidence score.
            prefer_us_format: Interpret MM/DD/YYYY as US format.
        """
        super().__init__(confidence=confidence)
        self._prefer_us = prefer_us_format
        months = self._month_pattern()
        self._compiled_patterns = [
            (re.compile(tmpl.format(months=months), re.IGNORECASE), fmt)
            for tmpl, fmt in self._DATE_PATTERN_TEMPLATES
        ]

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "date"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract dates from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for detected dates.
        """
        seen = set()

        for pattern, fmt in self._compiled_patterns:
            for match in pattern.finditer(text):
                date_str = match.group()

                # Skip duplicates
                if date_str in seen:
                    continue
                seen.add(date_str)

                # Parse date components
                parsed = self._parse_date(match.groups(), fmt)
                if parsed is None:
                    continue

                month, day, year = parsed

                # Validate date
                if not self._is_valid_date(month, day, year):
                    continue

                yield Entity(
                    value=date_str,
                    entity_type="date",
                    source_text=text,
                    confidence=self.confidence,
                    data={
                        "month": month,
                        "day": day,
                        "year": year,
                        "format": fmt,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

    def _parse_date(self, groups: tuple, fmt: str) -> tuple[int, int, int] | None:
        """Parse date groups into month, day, year.

        Args:
            groups: Regex match groups.
            fmt: Date format type.

        Returns:
            Tuple of (month, day, year) or None if invalid.
        """
        try:
            if fmt == 'ISO':
                # YYYY-MM-DD
                return int(groups[1]), int(groups[2]), int(groups[0])

            elif fmt == 'US':
                # MM/DD/YYYY or MM-DD-YYYY
                month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                if self._prefer_us and month > 12:
                    # Swap if invalid US format
                    month, day = day, month
                return month, day, year

            elif fmt == 'WRITTEN_US':
                # Month DD, YYYY
                month = self.MONTHS.get(groups[0].lower())
                day = int(groups[1])
                year = int(groups[2])
                return month, day, year

            elif fmt == 'WRITTEN_EU':
                # DD Month YYYY
                day = int(groups[0])
                month = self.MONTHS.get(groups[1].lower())
                year = int(groups[2])
                return month, day, year

        except (ValueError, TypeError):
            return None

        return None

    def _is_valid_date(self, month: int, day: int, year: int) -> bool:
        """Validate date components.

        Args:
            month: Month (1-12).
            day: Day (1-31).
            year: Year.

        Returns:
            True if valid date.
        """
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        if year < 1900 or year > 2100:
            return False

        # Check days in month
        days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if day > days_in_month[month - 1]:
            return False

        # February leap year check
        if month == 2 and day == 29:
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            if not is_leap:
                return False

        return True


if __name__ == "__main__":
    ner = DateAnnotator()
    text = """
    Meeting scheduled for 12/25/2024.
    Deadline: 2024-01-15 (ISO format).
    Event on January 5, 2025 or maybe 5 Jan 2025.
    Conference: 15/03/2025 (EU format).
    """

    print(f"Text: {text.strip()}")
    print("-" * 60)

    for ent in ner.extract_entities(text):
        data = ent.data
        print(f"{ent.value:20} -> {data['month']:2}/{data['day']:2}/{data['year']} ({data['format']})")
