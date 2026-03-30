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

    # Amount pattern fragment
    _AMT = r'(?:\d{1,3}(?:[,\s]\d{3})*|\d+)(?:[.,]\d{1,2})?'

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
            rf'(?:(?:{sym_alt})\s*{amt})'           # Symbol then amount
            rf'|(?:{amt}\s*(?:{iso_codes}))'         # Amount then ISO code
            rf'|(?:(?:{iso_codes})\s+{amt})'         # ISO code then amount
            rf'|(?:\b{amt}\s+(?:{written})\b)',      # Amount then written word
            re.IGNORECASE,
        )

    CURRENCY_PATTERN: re.Pattern[str] = None  # type: ignore[assignment]  # set below

    def __init__(self, confidence: float = 0.9) -> None:
        """Initialize CurrencyAnnotator.

        Args:
            confidence: Default confidence score.
        """
        super().__init__(confidence=confidence)

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
        for match in self.CURRENCY_PATTERN.finditer(text):
            money = match.group()
            currency, amount = self._parse_currency(money)

            if currency and amount:
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

    def _parse_currency(self, text: str) -> tuple[str | None, float | None]:
        """Parse currency string into currency code and amount.

        Args:
            text: Currency string (e.g., "$100", "USD 100").

        Returns:
            Tuple of (currency_code, amount).
        """
        # Clean and normalize
        text = text.strip()

        # Extract amount (remove non-numeric except decimal)
        amount_str = re.sub(r'[^\d.]', '', text)
        try:
            amount = float(amount_str)
        except ValueError:
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
