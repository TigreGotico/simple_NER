"""Unit tests for the annotator factory and pipeline integration."""
import pytest

from simple_NER.annotators.factory import (
    create_pipeline,
    get_annotator,
    list_available_annotators,
    register_annotator,
)


class TestAnnotatorFactory:
    """Tests for the annotator factory."""

    def test_list_available_annotators(self):
        """Test that we can list available annotators."""
        annotators = list_available_annotators()
        assert isinstance(annotators, list)
        assert len(annotators) > 0
        # Should be sorted
        assert annotators == sorted(annotators)
        # Should have core annotators
        assert "email" in annotators
        assert "names" in annotators

    def test_get_email_annotator(self):
        """Test getting email annotator."""
        annotator = get_annotator("email")
        assert annotator.name == "email"

    def test_get_names_annotator(self):
        """Test getting names annotator."""
        annotator = get_annotator("names")
        assert annotator.name == "names"

    def test_get_annotator_with_kwargs(self):
        """Test getting annotator with constructor arguments."""
        annotator = get_annotator("names", confidence=0.9)
        assert annotator.confidence == 0.9

    def test_get_unknown_annotator_raises(self):
        """Test that unknown annotator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown annotator"):
            get_annotator("nonexistent_annotator")

    def test_register_custom_annotator(self):
        """Test registering a custom annotator."""
        from collections.abc import Generator

        from simple_NER import Entity
        from simple_NER.annotators.base import BaseAnnotator

        class CustomAnnotator(BaseAnnotator):
            @property
            def name(self) -> str:
                return "custom_test"

            def annotate(self, text: str) -> Generator[Entity, None, None]:
                if "test" in text.lower():
                    yield Entity("test", "test_entity", source_text=text)

        # Register
        register_annotator("custom_test", CustomAnnotator)

        # Should be in list
        assert "custom_test" in list_available_annotators()

        # Should be creatable
        annotator = get_annotator("custom_test")
        assert isinstance(annotator, CustomAnnotator)

        # Should work
        results = list(annotator.extract_entities("this is a test"))
        assert len(results) == 1


class TestPipelineFactory:
    """Tests for the pipeline factory function."""

    def test_create_pipeline_basic(self):
        """Test creating a basic pipeline."""
        pipeline = create_pipeline(["email"])
        assert len(pipeline.annotators) == 1

    def test_create_pipeline_multiple(self):
        """Test creating pipeline with multiple annotators."""
        pipeline = create_pipeline(["email", "names"])
        assert len(pipeline.annotators) == 2

    def test_create_pipeline_with_dedup(self):
        """Test creating pipeline with deduplication strategy."""
        pipeline = create_pipeline(
            ["email", "names"],
            dedup_strategy="keep_higher_confidence",
        )
        assert pipeline.dedup_strategy == "keep_higher_confidence"

    def test_create_pipeline_invalid_annotator(self):
        """Test that invalid annotator is skipped with warning."""
        # Should not raise, just skip invalid ones
        pipeline = create_pipeline(["email", "nonexistent"])
        assert len(pipeline.annotators) >= 1  # At least email

    def test_create_pipeline_all_invalid_raises(self):
        """Test that all invalid annotators raises ValueError."""
        with pytest.raises(ValueError, match="No valid annotators"):
            create_pipeline(["nonexistent1", "nonexistent2"])

    def test_create_pipeline_with_kwargs(self):
        """Test creating pipeline with default kwargs."""
        pipeline = create_pipeline(["names"], confidence=0.85)
        # The annotator should receive the kwarg
        assert pipeline.annotators[0].confidence == 0.85


class TestPipelineIntegration:
    """Integration tests for pipeline with various annotators."""

    def test_pipeline_email_detection(self):
        """Test pipeline with email detection."""
        pipeline = create_pipeline(["email"])
        results = pipeline.process("Contact test@example.com")

        assert len(results) == 1
        assert results[0].value == "test@example.com"
        assert results[0].entity_type == "email"

    def test_pipeline_names_detection(self):
        """Test pipeline with names detection."""
        pipeline = create_pipeline(["names"])
        results = pipeline.process("John Doe met Alice")

        names = {r.value for r in results}
        # Names pattern captures full names like "John Doe"
        assert "John Doe" in names or "John" in names or "Alice" in names

    def test_pipeline_combined(self):
        """Test pipeline with multiple annotators."""
        pipeline = create_pipeline(["email", "names"])
        results = pipeline.process("John contacted john@test.com")

        types = {r.entity_type for r in results}
        assert "email" in types

    def test_pipeline_dedup_keep_all(self):
        """Test pipeline with keep_all deduplication."""
        from simple_NER.annotators.email_ner import EmailAnnotator
        from simple_NER.pipeline import NERPipeline

        pipeline = NERPipeline(
            [EmailAnnotator()],
            dedup_strategy="keep_all",
        )
        results = pipeline.process("Email test@example.com")

        assert len(results) == 1

    def test_pipeline_dedup_keep_longest(self):
        """Test pipeline with keep_longest deduplication."""
        from simple_NER.annotators.email_ner import EmailAnnotator
        from simple_NER.pipeline import NERPipeline

        pipeline = NERPipeline(
            [EmailAnnotator()],
            dedup_strategy="keep_longest",
        )
        results = pipeline.process("Email test@example.com")

        assert len(results) == 1

    def test_pipeline_dedup_keep_higher_confidence(self):
        """Test pipeline with keep_higher_confidence deduplication."""
        from simple_NER.annotators.email_ner import EmailAnnotator
        from simple_NER.pipeline import NERPipeline

        pipeline = NERPipeline(
            [EmailAnnotator()],
            dedup_strategy="keep_higher_confidence",
        )
        results = pipeline.process("Email test@example.com")

        assert len(results) == 1

    def test_pipeline_empty_text(self):
        """Test pipeline with empty text."""
        pipeline = create_pipeline(["email"])
        results = pipeline.process("")

        assert len(results) == 0

    def test_pipeline_no_matches(self):
        """Test pipeline with text that has no matches."""
        pipeline = create_pipeline(["email"])
        results = pipeline.process("This text has no email addresses")

        assert len(results) == 0


class TestFactoryEdgeCases:
    """Test edge cases in the factory."""

    def test_case_insensitive_lookup(self):
        """Test that annotator lookup is case-insensitive."""
        # Should work with different cases
        annotator1 = get_annotator("email")
        annotator2 = get_annotator("EMAIL")
        annotator3 = get_annotator("EmAiL")

        assert type(annotator1) is type(annotator2)
        assert type(annotator2) is type(annotator3)

    def test_register_duplicate_overwrites(self):
        """Test that registering duplicate name overwrites."""
        from collections.abc import Generator

        from simple_NER import Entity
        from simple_NER.annotators.base import BaseAnnotator

        class FirstAnnotator(BaseAnnotator):
            @property
            def name(self) -> str:
                return "overwrite_test"

            def annotate(self, text: str) -> Generator[Entity, None, None]:
                yield from []

        class SecondAnnotator(BaseAnnotator):
            @property
            def name(self) -> str:
                return "overwrite_test"

            def annotate(self, text: str) -> Generator[Entity, None, None]:
                yield from []

        register_annotator("overwrite_test", FirstAnnotator)
        register_annotator("overwrite_test", SecondAnnotator)

        # Should get the second one
        annotator = get_annotator("overwrite_test")
        assert isinstance(annotator, SecondAnnotator)
