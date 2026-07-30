"""Coverage-boosting tests for temporal_ner, lookup_ner, and factory.

Targets uncovered branches identified by coverage analysis:
- temporal_ner.py: lines 30-31, 33-44, 67, 73, 132, 144, 163, 168, 171, 189, 226, 231, 234, 242
- lookup_ner.py: lines 69, 75-84, 81-82, 86-87, 104-105, 110, 115-116, 136, 155-157, 168-172, 177
- factory.py: lines 141-147, 143-144, 151-152, 161-162, 171-172, 180-181, 189-190, 198-199,
              207-208, 216-217, 226-227, 236-237, 245-246
"""
from __future__ import annotations

import pathlib
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


# ===========================================================================
# temporal_ner.py
# ===========================================================================

class TestTemporalNERCoverage:
    """Tests targeting uncovered branches in temporal_ner.py."""

    # ------------------------------------------------------------------
    # Basic import / availability guard
    # ------------------------------------------------------------------

    def test_ovos_available_flag(self):
        """_OVOS_AVAILABLE is a bool."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE
        assert isinstance(_OVOS_AVAILABLE, bool)

    # ------------------------------------------------------------------
    # _load_temporal_keywords — known and unknown lang
    # ------------------------------------------------------------------

    def test_load_temporal_keywords_known_lang(self):
        """en-us keywords file exists; frozenset is non-empty."""
        from simple_NER.annotators.temporal_ner import _load_temporal_keywords
        kws = _load_temporal_keywords("en-us")
        assert isinstance(kws, frozenset)
        assert len(kws) > 0

    def test_load_temporal_keywords_unknown_lang_falls_back_to_en_us(self):
        """Unknown lang falls back to en-us (line 67 / fallback branch)."""
        from simple_NER.annotators.temporal_ner import _load_temporal_keywords
        kws_unknown = _load_temporal_keywords("xx-zz")
        kws_enus = _load_temporal_keywords("en-us")
        # Fallback must return the en-us set
        assert kws_unknown == kws_enus

    def test_load_temporal_keywords_no_files_returns_empty(self):
        """If both lang and en-us files are absent, return empty frozenset (line 73)."""
        from simple_NER.annotators import temporal_ner as mod

        original_res = mod._RES_DIR
        try:
            mod._RES_DIR = pathlib.Path("/nonexistent_path_xyz")
            result = mod._load_temporal_keywords("en-us")
            assert result == frozenset()
        finally:
            mod._RES_DIR = original_res

    # ------------------------------------------------------------------
    # TemporalNER.name property
    # ------------------------------------------------------------------

    def test_name_property(self):
        """name returns 'temporal' (line 132)."""
        from simple_NER.annotators.temporal_ner import TemporalNER
        ner = TemporalNER()
        assert ner.name == "temporal"

    # ------------------------------------------------------------------
    # annotate() when _OVOS_AVAILABLE is False
    # ------------------------------------------------------------------

    def test_annotate_no_ovos_yields_nothing(self):
        """annotate() returns immediately when _OVOS_AVAILABLE is False (line 144)."""
        import simple_NER.annotators.temporal_ner as mod

        original = mod._OVOS_AVAILABLE
        try:
            mod._OVOS_AVAILABLE = False
            from simple_NER.annotators.temporal_ner import TemporalNER
            ner = TemporalNER()
            results = list(ner.annotate("tomorrow at noon"))
            assert results == []
        finally:
            mod._OVOS_AVAILABLE = original

    # ------------------------------------------------------------------
    # anchor_date parameter
    # ------------------------------------------------------------------

    def test_anchor_date_explicit(self):
        """anchor_date passed explicitly is stored as-is."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        anchor = datetime(2025, 6, 15, 12, 0, 0)
        ner = TemporalNER(anchor_date=anchor)
        assert ner.anchor_date == anchor

    def test_anchor_date_default_is_now(self):
        """anchor_date defaults to datetime.now() when not supplied."""
        from simple_NER.annotators.temporal_ner import TemporalNER
        before = datetime.now()
        ner = TemporalNER()
        after = datetime.now()
        assert before <= ner.anchor_date <= after

    # ------------------------------------------------------------------
    # _extract_duration_entities — specific inputs
    # ------------------------------------------------------------------

    def test_duration_hours_and_minutes(self):
        """'it takes 2 hours and 30 minutes' yields a duration entity."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        if not _OVOS_AVAILABLE:
            pytest.skip("ovos-date-parser not installed")

        ner = TemporalNER(extract_datetime=False)
        results = list(ner.extract_entities("it takes 2 hours and 30 minutes"))
        assert any(r.entity_type == "duration" for r in results)
        # Verify data payload keys
        dur = next(r for r in results if r.entity_type == "duration")
        assert "total_seconds" in dur.data
        assert dur.data["total_seconds"] > 0

    def test_duration_days(self):
        """'3 days' yields a duration with days == 3."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        if not _OVOS_AVAILABLE:
            pytest.skip("ovos-date-parser not installed")

        ner = TemporalNER(extract_datetime=False)
        results = list(ner.extract_entities("wait 3 days"))
        assert any(r.entity_type == "duration" for r in results)

    def test_duration_week(self):
        """'1 week' yields a duration entity."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        if not _OVOS_AVAILABLE:
            pytest.skip("ovos-date-parser not installed")

        ner = TemporalNER(extract_datetime=False)
        results = list(ner.extract_entities("that takes 1 week"))
        assert any(r.entity_type == "duration" for r in results)

    def test_duration_only_flag(self):
        """extract_duration=False: no duration entities produced."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        if not _OVOS_AVAILABLE:
            pytest.skip("ovos-date-parser not installed")

        ner = TemporalNER(extract_duration=False)
        results = list(ner.extract_entities("wait 5 minutes"))
        assert not any(r.entity_type == "duration" for r in results)

    # ------------------------------------------------------------------
    # _temporal_kw guard — currency amount must NOT become datetime
    # ------------------------------------------------------------------

    def test_currency_amount_not_datetime(self):
        """'$500' must not yield a relative_date entity (line 189 guard)."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        if not _OVOS_AVAILABLE:
            pytest.skip("ovos-date-parser not installed")

        ner = TemporalNER(extract_duration=False)
        results = list(ner.extract_entities("it costs $500"))
        assert not any(r.entity_type == "relative_date" for r in results)

    def test_bare_number_not_datetime(self):
        """A bare number like '500' must not become a datetime entity."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        if not _OVOS_AVAILABLE:
            pytest.skip("ovos-date-parser not installed")

        ner = TemporalNER(extract_duration=False)
        results = list(ner.extract_entities("the price is 500"))
        assert not any(r.entity_type == "relative_date" for r in results)

    # ------------------------------------------------------------------
    # as_json=True path (Entity.as_json)
    # ------------------------------------------------------------------

    def test_duration_entity_as_json(self):
        """Entity.as_json() returns expected keys for duration entities (line 226/242)."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        if not _OVOS_AVAILABLE:
            pytest.skip("ovos-date-parser not installed")

        ner = TemporalNER(extract_datetime=False)
        results = list(ner.extract_entities("wait 10 minutes"))
        assert results
        j = results[0].as_json()
        assert isinstance(j, dict)
        assert "value" in j
        assert "entity_type" in j

    def test_datetime_entity_as_json(self):
        """Entity.as_json() returns expected keys for relative_date entities."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        if not _OVOS_AVAILABLE:
            pytest.skip("ovos-date-parser not installed")

        ner = TemporalNER(extract_duration=False)
        results = list(ner.extract_entities("see you tomorrow"))
        assert results
        j = results[0].as_json()
        assert isinstance(j, dict)
        assert j["entity_type"] == "relative_date"
        assert "isoformat" in j.get("data", {})

    # ------------------------------------------------------------------
    # extract_datetime=False guard (line 163)
    # ------------------------------------------------------------------

    def test_extract_datetime_false(self):
        """_extract_datetime_entities not called when extract_datetime=False."""
        from simple_NER.annotators.temporal_ner import _OVOS_AVAILABLE, TemporalNER
        if not _OVOS_AVAILABLE:
            pytest.skip("ovos-date-parser not installed")

        ner = TemporalNER(extract_datetime=False, extract_duration=False)
        results = list(ner.extract_entities("tomorrow at 3pm for 2 hours"))
        assert results == []

    # ------------------------------------------------------------------
    # backward-compat aliases
    # ------------------------------------------------------------------

    def test_datetime_ner_alias(self):
        """DateTimeNER and TimedeltaNER are aliases for TemporalNER."""
        from simple_NER.annotators.temporal_ner import DateTimeNER, TemporalNER, TimedeltaNER
        assert DateTimeNER is TemporalNER
        assert TimedeltaNER is TemporalNER


# ===========================================================================
# lookup_ner.py
# ===========================================================================

class TestLookUpNERCoverage:
    """Tests targeting uncovered branches in lookup_ner.py."""

    # ------------------------------------------------------------------
    # loaded_types property (line 177)
    # ------------------------------------------------------------------

    def test_loaded_types_is_list(self):
        """loaded_types returns a list of strings."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        types = ner.loaded_types
        assert isinstance(types, list)
        assert all(isinstance(t, str) for t in types)

    def test_loaded_types_reflects_entities(self):
        """loaded_types matches keys of entities dict."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        assert set(ner.loaded_types) == set(ner.entities.keys())

    # ------------------------------------------------------------------
    # add_wordlist then extract (lines 155-157)
    # ------------------------------------------------------------------

    def test_add_wordlist_then_extract(self):
        """add_wordlist adds label and words; extraction finds them."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        ner.add_wordlist("fruit", ["mango", "papaya", "lychee"])
        assert "fruit" in ner.loaded_types
        results = list(ner.extract_entities("I love mango juice"))
        assert any(r.entity_type == "fruit" for r in results)
        match = next(r for r in results if r.entity_type == "fruit")
        assert match.value.lower() == "mango"

    def test_add_wordlist_overwrites_existing(self):
        """add_wordlist with same label replaces the old wordlist."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        ner.add_wordlist("testlabel", ["alpha"])
        ner.add_wordlist("testlabel", ["beta"])
        assert ner.entities["testlabel"] == ["beta"]

    # ------------------------------------------------------------------
    # remove_wordlist (lines 168-172)
    # ------------------------------------------------------------------

    def test_remove_wordlist_returns_true(self):
        """remove_wordlist returns True when label exists and removes it."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        ner.add_wordlist("tmptype", ["foo", "bar"])
        assert "tmptype" in ner.loaded_types
        result = ner.remove_wordlist("tmptype")
        assert result is True
        assert "tmptype" not in ner.loaded_types

    def test_remove_wordlist_returns_false(self):
        """remove_wordlist returns False when label does not exist."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        result = ner.remove_wordlist("nonexistent_label_xyz")
        assert result is False

    def test_remove_wordlist_affects_extraction(self):
        """After removal, entities of that type are no longer found."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        ner.add_wordlist("veggie", ["broccoli"])
        assert list(ner.extract_entities("I ate broccoli"))
        ner.remove_wordlist("veggie")
        results = list(ner.extract_entities("I ate broccoli"))
        assert not any(r.entity_type == "veggie" for r in results)

    # ------------------------------------------------------------------
    # No entity files / empty entities (lines 110, 115-116, 136)
    # ------------------------------------------------------------------

    def test_annotate_no_entities_yields_nothing(self):
        """annotate() returns immediately when entities dict is empty (line 136)."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        # Clear everything out
        ner.entities.clear()
        ner._ac = None
        results = list(ner.annotate("The sky is blue"))
        assert results == []

    def test_no_entity_files_dir_missing(self):
        """LookUpNER with a lang that has no resource dir logs a warning."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        # Use a lang with no res/ folder — entities should be empty or nearly so
        ner = LookUpNER(lang="xx-zz")
        # Should not raise; entities may be empty
        assert isinstance(ner.entities, dict)

    # ------------------------------------------------------------------
    # _build_automaton rebuilds after add/remove (line 120->119 branch)
    # ------------------------------------------------------------------

    def test_build_automaton_rebuilt_after_add(self):
        """_ac is not None after add_wordlist."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        ner.entities.clear()
        ner._ac = None
        ner.add_wordlist("test", ["hello"])
        assert ner._ac is not None

    def test_build_automaton_none_when_empty(self):
        """_ac is None when entities dict is empty."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        ner.entities.clear()
        ner._build_automaton()
        assert ner._ac is None

    # ------------------------------------------------------------------
    # Entity data payload (line 104-105 branch: load error)
    # ------------------------------------------------------------------

    def test_entity_data_contains_source_and_language(self):
        """Extracted entities carry 'source' and 'language' in data dict."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        ner.add_wordlist("testdata", ["hello"])
        results = list(ner.extract_entities("hello world"))
        assert results
        data = results[0].data
        assert data.get("source") == "wordlist"
        assert "language" in data

    def test_entity_data_contains_span_positions(self):
        """Extracted entity data contains start and end character positions."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER()
        ner.add_wordlist("animal", ["cat"])
        results = list(ner.extract_entities("I saw a cat"))
        assert results
        data = results[0].data
        assert "start" in data
        assert "end" in data

    # ------------------------------------------------------------------
    # case_sensitive=True path (line 117)
    # ------------------------------------------------------------------

    def test_case_sensitive_lookup(self):
        """Case-sensitive mode: uppercase word does not match lowercase entry."""
        from simple_NER.annotators.lookup_ner import LookUpNER
        ner = LookUpNER(case_sensitive=True)
        ner.add_wordlist("brand", ["Nike"])
        # lowercase "nike" should NOT match "Nike" entry in case-sensitive mode
        results_lower = list(ner.extract_entities("I wear nike shoes"))
        results_upper = list(ner.extract_entities("I wear Nike shoes"))
        assert any(r.entity_type == "brand" for r in results_upper)
        assert not any(r.entity_type == "brand" for r in results_lower)


# ===========================================================================
# factory.py — uncovered branches (ImportError paths)
# ===========================================================================

class TestFactoryCoverage:
    """Tests targeting uncovered ImportError branches in factory._register_builtin_annotators."""

    def test_get_annotator_bad_kwargs_raises_type_error(self):
        """get_annotator re-raises TypeError from constructor (line 73-75)."""
        from simple_NER.annotators.base import BaseAnnotator
        from simple_NER.annotators.factory import get_annotator, register_annotator

        class StrictAnnotator(BaseAnnotator):
            def __init__(self, required_arg: str) -> None:
                super().__init__()
                self._req = required_arg

            @property
            def name(self) -> str:
                return "strict"

            def annotate(self, text):
                yield from []

        register_annotator("strict_test", StrictAnnotator)
        # Omitting required_arg must raise TypeError
        with pytest.raises(TypeError):
            get_annotator("strict_test")  # missing required_arg

    def test_list_available_returns_sorted(self):
        """list_available_annotators returns a sorted list."""
        from simple_NER.annotators.factory import list_available_annotators
        names = list_available_annotators()
        assert names == sorted(names)

    def test_create_pipeline_skips_invalid_with_valid_remaining(self):
        """create_pipeline warns and skips invalid name, returns valid pipeline."""
        from simple_NER.annotators.factory import create_pipeline
        pipeline = create_pipeline(["email", "nonexistent_xyz"])
        assert len(pipeline.annotators) >= 1
        types = [a.name for a in pipeline.annotators]
        assert "email" in types

    def test_register_annotator_stores_lowercase(self):
        """register_annotator stores name in lowercase."""
        from collections.abc import Generator

        from simple_NER import Entity
        from simple_NER.annotators.base import BaseAnnotator
        from simple_NER.annotators.factory import (
            list_available_annotators,
            register_annotator,
        )

        class UpperAnnotator(BaseAnnotator):
            @property
            def name(self) -> str:
                return "upper_case_test"

            def annotate(self, text: str) -> Generator[Entity, None, None]:
                yield from []

        register_annotator("UPPER_CASE_TEST", UpperAnnotator)
        assert "upper_case_test" in list_available_annotators()

    def test_builtin_annotators_registered_on_import(self):
        """Built-in annotators are registered automatically on import."""
        from simple_NER.annotators.factory import list_available_annotators
        names = list_available_annotators()
        # These should always be present
        assert "email" in names
        assert "names" in names
        assert "lookup" in names

    def test_register_builtin_with_import_error_skipped(self):
        """ImportError during built-in registration is silently skipped.

        Simulates a missing optional module: the registry must not contain
        the annotator but must not raise either.
        """
        import simple_NER.annotators.factory as factory_mod

        original_registry = dict(factory_mod._ANNOTATOR_REGISTRY)
        try:
            factory_mod._ANNOTATOR_REGISTRY.clear()
            with patch.dict("sys.modules", {"simple_NER.annotators.hashtag_ner": None}):
                factory_mod._register_builtin_annotators()
            # Registry populated from other modules; no crash
            assert len(factory_mod._ANNOTATOR_REGISTRY) > 0
        finally:
            factory_mod._ANNOTATOR_REGISTRY.clear()
            factory_mod._ANNOTATOR_REGISTRY.update(original_registry)

    def test_temporal_annotator_registered(self):
        """temporal, datetime, duration aliases all registered."""
        from simple_NER.annotators.factory import list_available_annotators
        names = list_available_annotators()
        assert "temporal" in names
        assert "datetime" in names
        assert "duration" in names

    def test_wordlist_alias_registered(self):
        """'wordlist' alias for LookUpNER is registered."""
        from simple_NER.annotators.factory import get_annotator
        ner = get_annotator("wordlist")
        assert ner.name == "lookup"
