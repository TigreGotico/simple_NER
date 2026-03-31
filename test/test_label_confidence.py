"""Tests for per-label confidence — S-005 (LookUpNER and LocationNER)."""
import pytest


class TestLookUpNERLabelConfidence:
    """S-005 — LookUpNER per-label confidence overrides."""

    def test_default_confidence_applied(self) -> None:
        from simple_NER.annotators.lookup_ner import LookUpNER

        ner = LookUpNER(confidence=0.8)
        ner.entities.clear()
        ner.add_wordlist("color", ["blue", "red"])
        results = list(ner.extract_entities("the sky is blue"))
        assert results, "Expected at least one entity"
        assert results[0].confidence == pytest.approx(0.8)

    def test_label_confidence_override(self) -> None:
        from simple_NER.annotators.lookup_ner import LookUpNER

        ner = LookUpNER(confidence=1.0, label_confidence={"color": 0.7})
        ner.entities.clear()
        ner.add_wordlist("color", ["blue", "red"])
        ner.add_wordlist("fruit", ["apple"])
        results = {e.entity_type: e.confidence for e in ner.extract_entities("blue apple")}
        assert results["color"] == pytest.approx(0.7), "color should use label_confidence"
        assert results["fruit"] == pytest.approx(1.0), "fruit should use default confidence"

    def test_label_confidence_missing_label_uses_default(self) -> None:
        from simple_NER.annotators.lookup_ner import LookUpNER

        ner = LookUpNER(confidence=0.9, label_confidence={"color": 0.5})
        ner.entities.clear()
        ner.add_wordlist("color", ["green"])
        ner.add_wordlist("size", ["large"])
        results = {e.entity_type: e.confidence for e in ner.extract_entities("large green")}
        assert results["color"] == pytest.approx(0.5)
        assert results["size"] == pytest.approx(0.9)


class TestLocationNERLabelConfidence:
    """S-005 — LocationNER per-label confidence overrides."""

    def test_default_confidence_all_labels(self) -> None:
        from simple_NER.annotators.locations_ner import LocationNER

        ner = LocationNER(confidence=0.9, include_cities=False)
        results = list(ner.extract_entities("Lisbon is in Portugal"))
        assert results, "Expected location entities"
        for ent in results:
            assert ent.confidence == pytest.approx(0.9)

    def test_per_label_confidence_country(self) -> None:
        from simple_NER.annotators.locations_ner import LocationNER

        ner = LocationNER(
            confidence=0.9,
            include_cities=False,
            label_confidence={"Country": 0.95, "Capital City": 0.85},
        )
        results = {e.entity_type: e.confidence for e in ner.extract_entities("Lisbon is in Portugal")}
        if "Country" in results:
            assert results["Country"] == pytest.approx(0.95)
        if "Capital City" in results:
            assert results["Capital City"] == pytest.approx(0.85)

    def test_city_label_confidence(self) -> None:
        from simple_NER.annotators.locations_ner import LocationNER

        ner = LocationNER(
            confidence=0.9,
            include_countries=False,
            include_capitals=False,
            include_cities=True,
            label_confidence={"City": 0.7},
        )
        results = list(ner.extract_entities("I live in Paris"))
        city_results = [e for e in results if e.entity_type == "City"]
        assert city_results, "Expected City entity"
        assert city_results[0].confidence == pytest.approx(0.7)
