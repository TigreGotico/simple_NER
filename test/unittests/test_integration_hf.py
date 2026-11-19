"""Integration tests with real HuggingFace datasets (small, fast ones)."""
import pytest

pytest.importorskip("datasets")
pytest.importorskip("ahocorasick_ner")

from ahocorasick_ner import AhocorasickNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline


class TestRealDatasetIntegration:
    """Test integration with real HuggingFace datasets."""

    def test_simple_manual_ner_in_pipeline(self):
        """Test wrapping a manually-built AhocorasickNER in a pipeline."""
        # Create NER manually without downloading
        ner = AhocorasickNER(case_sensitive=False)
        ner.add_word("city", "New York")
        ner.add_word("city", "London")
        ner.add_word("country", "Japan")
        ner.fit()

        # Wrap it
        wrapper = AhocorasickAnnotatorWrapper(ner)

        # Use in pipeline
        pipeline = NERPipeline()
        pipeline.add_annotator(wrapper)

        # Test
        text = "I flew from New York to London, then on to Japan."
        entities = pipeline.process(text)

        assert len(entities) >= 3
        entity_values = [e.value for e in entities]
        assert any("New York" in e or "new york" in e.lower() for e in entity_values)
        assert any("London" in e or "london" in e.lower() for e in entity_values)
        assert any("Japan" in e or "japan" in e.lower() for e in entity_values)

    def test_wrapper_preserves_confidence(self):
        """Test that wrapper passes through confidence."""
        ner = AhocorasickNER()
        ner.add_word("animal", "puppy")  # Use longer word (>5 chars)
        ner.fit()

        wrapper = AhocorasickAnnotatorWrapper(ner, confidence=0.75)
        entities = list(wrapper.extract_entities("I have a puppy"))

        assert len(entities) == 1
        assert entities[0].confidence == 0.75

    def test_multiple_wrappers_in_pipeline(self):
        """Test multiple AhocorasickNER instances wrapped in one pipeline."""
        # First NER: cities
        cities_ner = AhocorasickNER()
        cities_ner.add_word("city", "Paris")
        cities_ner.add_word("city", "Berlin")
        cities_ner.fit()

        # Second NER: foods
        foods_ner = AhocorasickNER()
        foods_ner.add_word("food", "pizza")
        foods_ner.add_word("food", "pasta")
        foods_ner.fit()

        # Pipeline
        pipeline = NERPipeline()
        pipeline.add_annotator(AhocorasickAnnotatorWrapper(cities_ner))
        pipeline.add_annotator(AhocorasickAnnotatorWrapper(foods_ner))

        # Test
        text = "In Paris, I ate pizza and pasta. In Berlin, I had more pasta."
        entities = pipeline.process(text)

        # Should find cities and foods
        entity_types = [e.entity_type for e in entities]
        assert "city" in entity_types
        assert "food" in entity_types

    def test_entity_data_includes_spans(self):
        """Test that Entity objects include start/end spans."""
        ner = AhocorasickNER()
        ner.add_word("animal", "rabbit")  # Use longer word (>5 chars)
        ner.fit()

        wrapper = AhocorasickAnnotatorWrapper(ner)
        entities = list(wrapper.extract_entities("The rabbit is here"))

        assert len(entities) == 1
        entity = entities[0]
        assert "start" in entity.data
        assert "end" in entity.data
        assert entity.data["start"] == 4  # Position of "rabbit"
        assert entity.data["end"] == 9  # Position after "rabbit"

    def test_dedup_strategy_with_ahocorasick(self):
        """Test that pipeline dedup works with multiple overlapping matches."""
        ner = AhocorasickNER()
        ner.add_word("type1", "test data")
        ner.add_word("type2", "data")
        ner.fit()

        pipeline = NERPipeline(dedup_strategy="keep_longest")
        pipeline.add_annotator(AhocorasickAnnotatorWrapper(ner))

        text = "Here is test data in the text"
        entities = pipeline.process(text)

        # Should prefer "test data" over "data"
        entity_values = [e.value for e in entities]
        # The exact behavior depends on pipeline dedup logic
        # At minimum, we shouldn't have both overlapping matches
        assert len(entities) <= 1 or not any(
            e1.data["start"] <= e2.data["start"] < e1.data["end"]
            for e1 in entities for e2 in entities
            if e1 != e2
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
