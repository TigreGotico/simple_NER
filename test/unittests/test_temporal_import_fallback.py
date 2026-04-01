"""Tests for TemporalNER import-error fallback (lines 21-44 in temporal_ner.py)."""
import importlib
import sys
from unittest.mock import patch

import pytest


def _reload_temporal_ner():
    """Force a fresh import of temporal_ner with the current sys.modules state."""
    for key in list(sys.modules):
        if "temporal_ner" in key:
            del sys.modules[key]
    import simple_NER.annotators.temporal_ner as mod
    return mod


def test_temporal_ner_available_when_deps_present():
    """_OVOS_AVAILABLE is True in the normal test environment."""
    import simple_NER.annotators.temporal_ner as mod
    assert mod._OVOS_AVAILABLE is True


def test_temporal_ner_unavailable_when_ovos_date_parser_missing():
    """When ovos_date_parser is not importable, _OVOS_AVAILABLE is False and sentinels are None."""
    # Block ovos_date_parser by making it appear absent
    with patch.dict(sys.modules, {"ovos_date_parser": None}):
        mod = _reload_temporal_ner()
        assert mod._OVOS_AVAILABLE is False
        assert mod.extract_datetime is None
        assert mod.extract_duration is None
        assert mod.nice_date is None
        assert mod.nice_duration is None
        assert mod._convert_numbers is None


def test_temporal_ner_annotate_returns_empty_when_unavailable():
    """TemporalNER.annotate yields nothing (rather than crashing) when deps are absent."""
    with patch.dict(sys.modules, {"ovos_date_parser": None}):
        mod = _reload_temporal_ner()
        ner = mod.TemporalNER()
        results = list(ner.annotate("see you tomorrow"))
        assert results == []
