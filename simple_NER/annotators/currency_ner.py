"""Currency and money entity extraction.

This module provides extraction of monetary values from text.
"""
from __future__ import annotations

import re
from typing import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator


class CurrencyAnnotator(BaseAnnotator):
    """Extract currency/money values from text.

    Language support: currency symbols and ISO codes are language-agnostic.
    Written currency words are recognised in English, Spanish, French, German,
    Portuguese, Italian, and Dutch.

    This annotator identifies monetary values in various formats:
    - Symbol: $100, €50.99, £1,000
    - Code: USD 100, EUR 50, GBP 1000
    - Written: 100 dollars, 50 euros

    Example:
        ```python
        from simple_NER.annotators.currency_ner import CurrencyAnnotator

        ner = CurrencyAnnotator()
        text = "The product costs $99.99 or €85"
        for ent in ner.extract_entities(text):
            print(f"{ent.value} -> {ent.entity_type}")
        ```
    """

    # Currency symbols and their codes
    CURRENCY_SYMBOLS = {
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        '₹': 'INR',
        'R$': 'BRL',
        '₽': 'RUB',
        '₩': 'KRW',
        '₺': 'TRY',
        'A$': 'AUD',
        'C$': 'CAD',
    }

    # Written currency words → ISO code
    # en / es / fr / de / pt / it / nl
    WRITTEN_WORDS: dict[str, str] = {
        # USD
        'dollar': 'USD', 'dollars': 'USD',
        'dólar': 'USD', 'dólares': 'USD',          # es
        # EUR
        'euro': 'EUR', 'euros': 'EUR',
        'euro': 'EUR',                               # fr/de/it/nl (same)
        # GBP
        'pound': 'GBP', 'pounds': 'GBP',
        'libra': 'GBP', 'libras': 'GBP',           # es/pt
        'livre': 'GBP', 'livres': 'GBP',           # fr
        'pfund': 'GBP',                              # de
        # JPY
        'yen': 'JPY',
        # INR
        'rupee': 'INR', 'rupees': 'INR',
        'rupia': 'INR', 'rupias': 'INR',            # es/pt
        'roupie': 'INR', 'roupies': 'INR',          # fr
        'rupie': 'INR',                              # de/it
        # BRL
        'real': 'BRL', 'reais': 'BRL', 'reals': 'BRL',
        # CHF
        'franc': 'CHF', 'francs': 'CHF',
        'franco': 'CHF', 'francos': 'CHF',          # es/pt/it
        'frank': 'CHF', 'franken': 'CHF',           # de/nl
        # SEK/NOK/DKK (crown)
        'krona': 'SEK', 'kronor': 'SEK',
        'krone': 'NOK', 'kroner': 'NOK',
        'corona': 'SEK', 'coronas': 'SEK',          # es
        'couronne': 'SEK', 'couronnes': 'SEK',      # fr
        'krone': 'DKK', 'kroner': 'DKK',
    }

    # Amount pattern fragment — US (1,000.50), EU (1.000,50), or plain integer
    # Amount pattern fragment.
    # EU branch uses + (requires at least one dot-group) so it does not shadow
    # plain decimals; similarly US branch requires at least one comma-group.
    # Plain fallback handles bare integers and simple decimals (1.5, 1,5).
    _AMT = (
        r'(?:'
        r'\d{1,3}(?:\.\d{3})+(?:,\d+)?'   # EU: 1.000,50 (dot-thousands + comma-dec)
        r'|'
        r'\d{1,3}(?:,\d{3})+(?:\.\d+)?'   # US: 1,000.50 (comma-thousands + dot-dec)
        r'|\d+(?:[.,]\d+)?'                # plain: 50, 1.5, 1,5
        r')'
    )

    # Currency symbols split by length to avoid character-class bugs.
    # Multi-char symbols (R$, A$, C$) MUST use alternation, not [...].
    _MULTI_CHAR_SYMBOLS = ['R$', 'A$', 'C$']
    _SINGLE_CHAR_SYMBOLS = [s for s in CURRENCY_SYMBOLS.keys() if len(s) == 1]

    @classmethod
    def _build_pattern(cls) -> re.Pattern[str]:
        """Build the currency regex pattern at class definition time."""
        amt = cls._AMT
        # Longest multi-char symbols first, then single-char symbols in a set
        sym_alt = (
            '|'.join(re.escape(s) for s in cls._MULTI_CHAR_SYMBOLS)
            + '|'
            + '[' + ''.join(re.escape(s) for s in cls._SINGLE_CHAR_SYMBOLS) + ']'
        )
        iso_codes = '|'.join(cls.CURRENCY_SYMBOLS.values())
        written = '|'.join(sorted(cls.WRITTEN_WORDS.keys(), key=len, reverse=True))
        return re.compile(
            rf'(?:(?:{sym_alt})\s*{amt})'            # Symbol then amount: €1.000,50
            rf'|(?:{amt}\s*(?:{sym_alt}))'            # Amount then symbol: 1.000,50 €
            rf'|(?:{amt}\s*(?:{iso_codes}))'          # Amount then ISO code: 1.000,50 EUR
            rf'|(?:(?:{iso_codes})\s+{amt})'          # ISO code then amount: EUR 1.000,50
            rf'|(?:\b{amt}\s+(?:{written})\b)',       # Amount then written word: 50 euros
            re.IGNORECASE,
        )

    CURRENCY_PATTERN: re.Pattern[str] = None  # type: ignore[assignment]  # set below

    def __init__(self, confidence: float = 0.9) -> None:
        """Initialize CurrencyAnnotator.

        Args:
            confidence: Default confidence score.
        """
        super().__init__(confidence=confidence)
        self._intent_patterns = self._load_intents("currency")

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "currency"

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract currency values from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for detected monetary values.
        """
        seen_spans: list[tuple[int, int]] = []

        for match in self.CURRENCY_PATTERN.finditer(text):
            money = match.group()
            currency, amount = self._parse_currency(money)

            if currency and amount:
                seen_spans.append((match.start(), match.end()))
                yield Entity(
                    value=money,
                    entity_type="money",
                    source_text=text,
                    confidence=self.confidence,
                    data={
                        "amount": amount,
                        "currency": currency,
                        "currency_symbol": self._get_symbol(currency),
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

        for pat in self._intent_patterns:
            for m in pat.finditer(text):
                # Skip if this span overlaps with an already-yielded entity
                if any(m.start() < e and s < m.end() for s, e in seen_spans):
                    continue
                seen_spans.append((m.start(), m.end()))
                amount = m.group("amount") if "amount" in pat.groupindex else m.group()
                yield Entity(
                    m.group(),
                    "currency",
                    source_text=text,
                    confidence=self.confidence,
                    data={
                        "amount": amount,
                        "currency_type": "written",
                        "start": m.start(),
                        "end": m.end(),
                    }
                )

    @staticmethod
    def _normalize_amount(raw: str) -> float | None:
        """Normalize a raw amount string to float, handling US and EU formats.

        Args:
            raw: Raw amount string, e.g. "1,000.50" (US) or "1.000,50" (EU).

        Returns:
            Normalized float, or None on parse failure.
        """
        raw = raw.strip()
        # EU format: dot thousands groups then comma decimal, e.g. "1.000,50"
        if re.search(r'\d\.\d{3}', raw) and ',' in raw:
            raw = raw.replace('.', '').replace(',', '.')
        elif ',' in raw and '.' not in raw:
            # Bare comma decimal, e.g. "1,50"
            raw = raw.replace(',', '.')
        else:
            # US format: remove comma thousands separator
            raw = raw.replace(',', '')
        try:
            return float(raw)
        except ValueError:
            return None

    def _parse_currency(self, text: str) -> tuple[str | None, float | None]:
        """Parse currency string into currency code and amount.

        Args:
            text: Currency string (e.g., "$100", "USD 100").

        Returns:
            Tuple of (currency_code, amount).
        """
        # Clean and normalize
        text = text.strip()

        # Extract raw amount string (digits, commas, dots, spaces)
        amount_match = re.search(r'[\d][0-9,.\s]*', text)
        if amount_match:
            amount = self._normalize_amount(amount_match.group())
        else:
            amount = None
        if amount is None:
            return None, None

        # Detect currency
        currency = None

        # Check for symbol — longest first so "A$" beats "$"
        for symbol, code in sorted(self.CURRENCY_SYMBOLS.items(), key=lambda x: len(x[0]), reverse=True):
            if symbol in text:
                currency = code
                break

        # Check for ISO code
        if not currency:
            for code in self.CURRENCY_SYMBOLS.values():
                if code.upper() in text.upper():
                    currency = code.upper()
                    break

        # Check for written word (longest match first)
        if not currency:
            text_lower = text.lower()
            for word in sorted(self.WRITTEN_WORDS, key=len, reverse=True):
                if word in text_lower:
                    currency = self.WRITTEN_WORDS[word]
                    break

        # Default to USD if no currency found but has $
        if not currency and '$' in text:
            currency = 'USD'

        return currency, amount

    def _get_symbol(self, currency: str) -> str:
        """Get symbol for currency code.

        Args:
            currency: Currency code (e.g., "USD").

        Returns:
            Currency symbol.
        """
        for symbol, code in self.CURRENCY_SYMBOLS.items():
            if code == currency:
                return symbol
        return currency


CurrencyAnnotator.CURRENCY_PATTERN = CurrencyAnnotator._build_pattern()


if __name__ == "__main__":
    ner = CurrencyAnnotator()
    text = """
    The product costs $99.99 or €85.
    Price: USD 150, EUR 120, GBP 100
    Budget: £1,000.50 and ¥5000
    """

    print(f"Text: {text.strip()}")
    print("-" * 60)

    for ent in ner.extract_entities(text):
        data = ent.data
        print(f"{ent.value:15} -> {data['amount']:10.2f} {data['currency']}")
