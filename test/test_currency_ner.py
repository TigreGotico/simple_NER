"""Tests for CurrencyAnnotator — S-010 (EU decimal notation) and confidence."""
import pytest

from simple_NER.annotators.currency_ner import CurrencyAnnotator


class TestCurrencyNormalizeAmount:
    """Unit tests for _normalize_amount static method."""

    def test_us_format(self) -> None:
        assert CurrencyAnnotator._normalize_amount("1,000.50") == 1000.50

    def test_eu_format(self) -> None:
        assert CurrencyAnnotator._normalize_amount("1.000,50") == 1000.50

    def test_bare_comma_decimal(self) -> None:
        assert CurrencyAnnotator._normalize_amount("1,50") == 1.50

    def test_plain_integer(self) -> None:
        assert CurrencyAnnotator._normalize_amount("50") == 50.0

    def test_invalid_returns_none(self) -> None:
        assert CurrencyAnnotator._normalize_amount("abc") is None


class TestCurrencyEUFormat:
    """S-010 — European number format extraction."""

    def _ner(self) -> CurrencyAnnotator:
        return CurrencyAnnotator()

    def _match(self, text: str) -> dict:
        results = list(self._ner().extract_entities(text))
        assert results, f"No entity found in: {text!r}"
        return results[0].data

    def test_eu_amount_with_symbol_suffix(self) -> None:
        data = self._match("1.000,50 €")
        assert data["amount"] == pytest.approx(1000.50)
        assert data["currency"] == "EUR"

    def test_eu_amount_symbol_prefix(self) -> None:
        data = self._match("€ 2.500,00")
        assert data["amount"] == pytest.approx(2500.00)
        assert data["currency"] == "EUR"

    def test_eu_amount_iso_suffix(self) -> None:
        data = self._match("1.000,50 EUR")
        assert data["amount"] == pytest.approx(1000.50)
        assert data["currency"] == "EUR"

    def test_bare_comma_decimal_eur(self) -> None:
        data = self._match("1,50 EUR")
        assert data["amount"] == pytest.approx(1.50)
        assert data["currency"] == "EUR"

    def test_us_format_still_works(self) -> None:
        data = self._match("$1,000.50")
        assert data["amount"] == pytest.approx(1000.50)
        assert data["currency"] == "USD"

    def test_plain_integer_usd(self) -> None:
        data = self._match("50 USD")
        assert data["amount"] == pytest.approx(50.0)
        assert data["currency"] == "USD"

    def test_symbol_only_no_eu_grouping(self) -> None:
        data = self._match("€85")
        assert data["amount"] == pytest.approx(85.0)
        assert data["currency"] == "EUR"
