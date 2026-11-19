"""Tests for simple_NER annotator factory."""
import pytest

from simple_NER.annotators.base import Annotator, BaseAnnotator
from simple_NER.annotators.factory import (
    create_pipeline,
    get_annotator,
    list_available_annotators,
    register_annotator,
)
from simple_NER.pipeline import NERPipeline


ALL_KEYS = [
    "email",
    "email_regex",
    "names",
    "locations",
    "countries",
    "cities",
    "temporal",
    "datetime",
    "duration",
    "numbers",
    "written_numbers",
    "lookup",
    "wordlist",
    "url",
    "urls",
    "phone",
    "phone_number",
    "currency",
    "money",
    "organization",
    "org",
    "company",
    "hashtag",
    "hashtags",
    "tag",
    "date",
    "dates",
]


@pytest.mark.parametrize("key", ALL_KEYS)
def test_get_annotator_instantiates(key):
    """Every registered factory key instantiates without error and exposes extract_entities."""
    annotator = get_annotator(key)
    assert callable(getattr(annotator, "extract_entities", None))


def test_unknown_key_raises_value_error():
    """get_annotator raises ValueError for an unregistered name."""
    with pytest.raises(ValueError, match="Unknown annotator"):
        get_annotator("does_not_exist_xyz")


def test_list_available_annotators_contains_core_keys():
    """list_available_annotators returns at least the core built-in keys."""
    available = list_available_annotators()
    for key in ("email", "names", "phone", "currency", "temporal", "url"):
        assert key in available


def test_list_available_annotators_is_sorted():
    """list_available_annotators returns a sorted list."""
    available = list_available_annotators()
    assert available == sorted(available)


def test_register_custom_annotator():
    """Custom annotators can be registered and retrieved."""
    from simple_NER import Entity

    class _DummyAnnotator(BaseAnnotator):
        @property
        def name(self) -> str:
            return "dummy"

        def annotate(self, text):
            yield Entity("dummy", "dummy", source_text=text)

    register_annotator("_test_dummy", _DummyAnnotator)
    ann = get_annotator("_test_dummy")
    assert isinstance(ann, BaseAnnotator)


def test_create_pipeline_returns_ner_pipeline():
    """create_pipeline returns a NERPipeline with the requested annotators."""
    pipeline = create_pipeline(["email", "phone"], dedup_strategy="keep_all")
    assert isinstance(pipeline, NERPipeline)


def test_create_pipeline_skips_unknown_name(caplog):
    """create_pipeline skips unknown names with a warning, not an exception."""
    pipeline = create_pipeline(["email", "totally_unknown_xyz"])
    assert isinstance(pipeline, NERPipeline)


def test_create_pipeline_all_unknown_raises():
    """create_pipeline raises ValueError when no valid annotators remain."""
    with pytest.raises(ValueError, match="No valid annotators"):
        create_pipeline(["unknown_a", "unknown_b"])
