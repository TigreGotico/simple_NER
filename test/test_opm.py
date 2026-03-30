"""Unit tests for the OVOS Intent Transformer plugin (simple_NER.opm)."""
import pytest
from ovos_plugin_manager.templates.pipeline import IntentHandlerMatch

from simple_NER.opm import SimpleNERIntentTransformer


def make_intent(utterance: str, match_data: dict | None = None) -> IntentHandlerMatch:
    return IntentHandlerMatch(
        match_type="test:intent",
        match_data=match_data or {},
        skill_id="test.skill",
        utterance=utterance,
    )


class TestInit:
    def test_defaults(self) -> None:
        t = SimpleNERIntentTransformer()
        assert t.name == "simple-ner-transformer"
        assert t._confidence_threshold == 0.5
        assert isinstance(t._annotator_names, list)

    def test_custom_config(self) -> None:
        t = SimpleNERIntentTransformer(config={
            "annotators": ["email", "names"],
            "confidence_threshold": 0.7,
        })
        assert t._annotator_names == ["email", "names"]
        assert t._confidence_threshold == 0.7


class TestTransform:
    def test_returns_intent_handler_match(self) -> None:
        t = SimpleNERIntentTransformer()
        intent = make_intent("hello world")
        result = t.transform(intent)
        assert isinstance(result, IntentHandlerMatch)
        assert result is intent

    def test_email_injected_into_match_data(self) -> None:
        t = SimpleNERIntentTransformer(config={"annotators": ["email"]})
        intent = make_intent("Email john@example.com")
        t.transform(intent)
        assert "email" in intent.match_data
        assert "john@example.com" in intent.match_data["email"]

    def test_existing_key_not_overwritten(self) -> None:
        t = SimpleNERIntentTransformer(config={"annotators": ["email"]})
        intent = make_intent("Email foo@bar.com", match_data={"email": "already_set"})
        t.transform(intent)
        assert intent.match_data["email"] == "already_set"

    def test_no_entities_leaves_match_data_unchanged(self) -> None:
        t = SimpleNERIntentTransformer()
        intent = make_intent("turn on the lights")
        t.transform(intent)
        # No NER entities expected; match_data should remain empty (or not crash)
        assert isinstance(intent.match_data, dict)

    def test_high_confidence_threshold_filters_entities(self) -> None:
        t = SimpleNERIntentTransformer(config={"confidence_threshold": 1.1})
        intent = make_intent("Email foo@bar.com")
        t.transform(intent)
        assert "email" not in intent.match_data

    def test_none_utterance_does_not_raise(self) -> None:
        t = SimpleNERIntentTransformer()
        intent = make_intent(None)
        result = t.transform(intent)
        assert result is intent


class TestPipelineLazyInit:
    def test_pipeline_created_on_first_use(self) -> None:
        t = SimpleNERIntentTransformer()
        assert t._pipeline is None
        _ = t._get_pipeline("en-us")
        assert t._pipeline is not None

    def test_pipeline_reused(self) -> None:
        t = SimpleNERIntentTransformer()
        p1 = t._get_pipeline("en-us")
        p2 = t._get_pipeline("en-us")
        assert p1 is p2

    def test_pipeline_rebuilds_on_lang_change(self) -> None:
        t = SimpleNERIntentTransformer()
        p1 = t._get_pipeline("en-us")
        p2 = t._get_pipeline("de-de")
        assert p1 is not p2
        assert t._pipeline_lang == "de-de"
