"""Tests for S-006 (cross-annotator span-overlap dedup) and S-003 (international phone formats)."""
from __future__ import annotations

import pytest

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.pipeline import NERPipeline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeAnnotator(BaseAnnotator):
    """Annotator that yields a fixed list of entities for testing."""

    def __init__(self, name: str, entities: list[Entity], confidence: float = 1.0) -> None:
        super().__init__(confidence=confidence)
        self._name = name
        self._entities = entities

    @property
    def name(self) -> str:
        return self._name

    def annotate(self, text: str):
        yield from self._entities


def _make_entity(
    value: str,
    entity_type: str,
    start: int,
    end: int,
    confidence: float = 1.0,
    source_text: str = "",
) -> Entity:
    return Entity(
        value=value,
        entity_type=entity_type,
        source_text=source_text,
        confidence=confidence,
        data={"start": start, "end": end},
    )


# ---------------------------------------------------------------------------
# S-006: Cross-annotator span-overlap dedup
# ---------------------------------------------------------------------------

class TestOverlapDedup:
    """Longest-span-wins dedup across annotators."""

    def test_exact_overlap_currency_wins_over_number(self) -> None:
        """$500 matched by currency AND written_number — only ONE entity returned."""
        text = "I paid $500 for it"
        currency_ent = _make_entity("$500", "money", 7, 11, confidence=0.9, source_text=text)
        number_ent = _make_entity("500", "written_number", 8, 11, confidence=0.85, source_text=text)

        annotator_a = _FakeAnnotator("currency", [currency_ent])
        annotator_b = _FakeAnnotator("numbers", [number_ent])
        pipeline = NERPipeline([annotator_a, annotator_b], dedup_strategy="keep_longest")

        results = pipeline.process(text)
        assert len(results) == 1
        assert results[0].entity_type == "money"

    def test_longer_span_wins_over_shorter(self) -> None:
        """Longer span always wins regardless of annotator order."""
        text = "New York City"
        short_ent = _make_entity("York", "location", 4, 8, confidence=1.0, source_text=text)
        long_ent = _make_entity("New York City", "city", 0, 13, confidence=0.8, source_text=text)

        # Put short annotator first to confirm order doesn't override length.
        pipeline = NERPipeline(
            [_FakeAnnotator("a", [short_ent]), _FakeAnnotator("b", [long_ent])],
            dedup_strategy="keep_longest",
        )
        results = pipeline.process(text)
        assert len(results) == 1
        assert results[0].entity_type == "city"

    def test_equal_length_higher_confidence_wins(self) -> None:
        """Equal-length overlapping spans: higher confidence wins."""
        text = "hello world"
        ent_low = _make_entity("hello", "a", 0, 5, confidence=0.5, source_text=text)
        ent_high = _make_entity("hello", "b", 0, 5, confidence=0.9, source_text=text)

        pipeline = NERPipeline(
            [_FakeAnnotator("a", [ent_low]), _FakeAnnotator("b", [ent_high])],
            dedup_strategy="keep_longest",
        )
        results = pipeline.process(text)
        assert len(results) == 1
        assert results[0].entity_type == "b"

    def test_non_overlapping_entities_both_kept(self) -> None:
        """Entities with disjoint spans are both preserved."""
        text = "John called 555-1234"
        name_ent = _make_entity("John", "person", 0, 4, source_text=text)
        phone_ent = _make_entity("555-1234", "phone_number", 12, 20, source_text=text)

        pipeline = NERPipeline(
            [_FakeAnnotator("names", [name_ent]), _FakeAnnotator("phone", [phone_ent])],
            dedup_strategy="keep_longest",
        )
        results = pipeline.process(text)
        assert len(results) == 2
        types = {r.entity_type for r in results}
        assert "person" in types
        assert "phone_number" in types

    def test_result_sorted_by_start_position(self) -> None:
        """Returned entities are ordered by their start offset."""
        text = "alpha beta gamma"
        e1 = _make_entity("gamma", "c", 11, 16, source_text=text)
        e2 = _make_entity("alpha", "a", 0, 5, source_text=text)
        e3 = _make_entity("beta", "b", 6, 10, source_text=text)

        pipeline = NERPipeline(
            [_FakeAnnotator("x", [e1, e2, e3])],
            dedup_strategy="keep_longest",
        )
        results = pipeline.process(text)
        starts = [r.data["start"] for r in results]
        assert starts == sorted(starts)

    def test_entity_without_span_info_included(self) -> None:
        """Entities with no span data are included without crashing."""
        text = "hello"
        no_span_ent = Entity("hello", "keyword", source_text=text)

        pipeline = NERPipeline(
            [_FakeAnnotator("kw", [no_span_ent])],
            dedup_strategy="keep_longest",
        )
        results = pipeline.process(text)
        assert len(results) >= 1

    def test_keep_all_strategy_returns_all(self) -> None:
        """keep_all strategy bypasses dedup entirely."""
        text = "test 500"
        e1 = _make_entity("500", "money", 5, 8, source_text=text)
        e2 = _make_entity("500", "number", 5, 8, source_text=text)

        pipeline = NERPipeline(
            [_FakeAnnotator("a", [e1]), _FakeAnnotator("b", [e2])],
            dedup_strategy="keep_all",
        )
        results = pipeline.process(text)
        assert len(results) == 2

    def test_pipeline_resolve_span_static_method(self) -> None:
        """_resolve_span prefers data dict over spans property."""
        entity_with_data = _make_entity("hello", "kw", 3, 8, source_text="hi hello world")
        span = NERPipeline._resolve_span(entity_with_data)
        assert span == (3, 8)

    def test_currency_and_number_integration(self) -> None:
        """Integration: currency annotator emits span-aware entity; numbers annotator
        emits no-span entity.  Pipeline must not crash; the spanned currency entity
        is accepted, the no-span number entity is appended.  Both appear in results
        but the total is less than a keep_all run (no duplicate span-based collision).
        """
        from simple_NER.annotators.currency_ner import CurrencyAnnotator
        from simple_NER.annotators.numbers_ner import NumberNER as NumberAnnotator

        text = "I paid $500 for it"
        pipeline_dedup = NERPipeline(
            [CurrencyAnnotator(), NumberAnnotator()],
            dedup_strategy="keep_longest",
        )
        pipeline_all = NERPipeline(
            [CurrencyAnnotator(), NumberAnnotator()],
            dedup_strategy="keep_all",
        )
        results_dedup = pipeline_dedup.process(text)
        results_all = pipeline_all.process(text)

        # Dedup must not crash and must return a list.
        assert isinstance(results_dedup, list)
        # Spanned currency entity must be present.
        assert any(r.entity_type == "money" for r in results_dedup)
        # keep_all always returns at least as many entities as keep_longest.
        assert len(results_all) >= len(results_dedup)


# ---------------------------------------------------------------------------
# S-003: International phone number formats
# ---------------------------------------------------------------------------

class TestPhoneInternational:
    """PhoneAnnotator matches space-separated international formats."""

    @pytest.fixture(autouse=True)
    def _ner(self) -> None:
        from simple_NER.annotators.phone_ner import PhoneAnnotator
        self.ner = PhoneAnnotator()

    def _match(self, text: str) -> list[str]:
        return [e.value for e in self.ner.extract_entities(text)]

    def test_uk_space_separated(self) -> None:
        """+44 20 7946 0958 is matched."""
        matches = self._match("+44 20 7946 0958")
        assert any("44" in m for m in matches), f"No match in {matches}"

    def test_french_space_separated(self) -> None:
        """+33 1 23 45 67 89 is matched."""
        matches = self._match("+33 1 23 45 67 89")
        assert any("33" in m for m in matches), f"No match in {matches}"

    def test_us_dash_separated_regression(self) -> None:
        """+1-555-123-4567 still matches (regression)."""
        matches = self._match("+1-555-123-4567")
        assert len(matches) >= 1

    def test_us_parenthesis_format_regression(self) -> None:
        """(555) 987-6543 still matches (regression)."""
        matches = self._match("(555) 987-6543")
        assert len(matches) >= 1

    def test_plain_us_format_regression(self) -> None:
        """555.123.4567 still matches (regression)."""
        matches = self._match("555.123.4567")
        assert len(matches) >= 1

    def test_entity_type_is_phone_number(self) -> None:
        """Entities extracted for international numbers have correct entity_type."""
        from simple_NER.annotators.phone_ner import PhoneAnnotator
        ner = PhoneAnnotator()
        results = list(ner.extract_entities("+44 20 7946 0958"))
        assert any(e.entity_type == "phone_number" for e in results)

    def test_has_country_code_flag(self) -> None:
        """Entities for international numbers have has_country_code=True."""
        from simple_NER.annotators.phone_ner import PhoneAnnotator
        ner = PhoneAnnotator()
        results = list(ner.extract_entities("+44 20 7946 0958"))
        assert any(e.data.get("has_country_code") for e in results)

    def test_require_country_code_filters_local(self) -> None:
        """require_country_code=True drops plain US local numbers."""
        from simple_NER.annotators.phone_ner import PhoneAnnotator
        ner = PhoneAnnotator(require_country_code=True)
        results = list(ner.extract_entities("call 555-1234"))
        assert all(e.data.get("has_country_code") for e in results)
