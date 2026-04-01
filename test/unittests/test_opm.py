"""Tests for SimpleNERIntentTransformer (opm.py) — session/lang branch coverage."""
from unittest.mock import MagicMock, patch

import pytest


def _make_intent(utterance="reach me at foo@bar.com", match_data=None, lang=None):
    """Build a minimal mock IntentHandlerMatch."""
    intent = MagicMock()
    intent.utterance = utterance
    intent.match_data = match_data if match_data is not None else {}
    intent.updated_session = None
    if lang is not None:
        session = MagicMock()
        session.lang = lang
        intent.updated_session = session
    return intent


class TestSimpleNERIntentTransformer:
    def _make_transformer(self, annotators=("email",), config=None):
        from simple_NER.opm import SimpleNERIntentTransformer
        cfg = {"annotators": list(annotators), "confidence_threshold": 0.0, "lang": "en-us"}
        if config:
            cfg.update(config)
        return SimpleNERIntentTransformer(config=cfg)

    def test_transform_injects_entity(self):
        """transform() adds a recognised entity to match_data."""
        t = self._make_transformer(annotators=["email"])
        intent = _make_intent("reach me at foo@bar.com")
        result = t.transform(intent)
        assert result is intent
        assert "email" in result.match_data

    def test_transform_does_not_overwrite_existing_key(self):
        """transform() skips keys already present in match_data."""
        t = self._make_transformer(annotators=["email"])
        intent = _make_intent(match_data={"email": "already_set"})
        t.transform(intent)
        assert intent.match_data["email"] == "already_set"

    def test_transform_uses_session_lang(self):
        """transform() picks up lang from intent.updated_session when present."""
        t = self._make_transformer(annotators=["email"])
        intent = _make_intent("call me at 555-1234", lang="en-us")
        # session lang matches default — pipeline rebuilds; should still work
        result = t.transform(intent)
        assert result is intent

    def test_transform_falls_back_to_session_manager(self):
        """When updated_session is None, SessionManager.get() is tried (lines 127-130)."""
        from simple_NER.opm import SimpleNERIntentTransformer
        t = self._make_transformer(annotators=["email"])
        mock_session = MagicMock()
        mock_session.lang = "en-us"
        with patch("simple_NER.opm._SessionManager") as mock_sm:
            mock_sm.get.return_value = mock_session
            intent = _make_intent("reach me at foo@bar.com")
            intent.updated_session = None
            result = t.transform(intent)
        assert result is intent

    def test_transform_handles_session_manager_exception(self):
        """SessionManager.get() raising is swallowed; default lang is used (line 129-130)."""
        t = self._make_transformer(annotators=["email"])
        with patch("simple_NER.opm._SessionManager") as mock_sm:
            mock_sm.get.side_effect = RuntimeError("no session")
            intent = _make_intent("reach me at foo@bar.com")
            result = t.transform(intent)
        assert result is intent

    def test_transform_returns_intent_on_pipeline_error(self):
        """If the pipeline raises, transform() catches it and returns intent unchanged."""
        t = self._make_transformer(annotators=["email"])
        with patch.object(t, "_get_pipeline", side_effect=Exception("boom")):
            intent = _make_intent("reach me at foo@bar.com")
            result = t.transform(intent)
        assert result is intent
        assert result.match_data == {}
