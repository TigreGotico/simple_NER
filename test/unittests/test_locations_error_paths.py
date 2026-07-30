"""Tests for LocationNER error-handling branches (lines 131-145 in locations_ner.py)."""
from unittest.mock import MagicMock, patch

import pytest


def test_load_vocab_countries_json_decode_error(tmp_path):
    """OSError/JSONDecodeError on countries.json is caught; annotator still initialises."""
    from simple_NER.annotators.locations_ner import LocationNER

    bad_json = tmp_path / "countries.json"
    bad_json.write_text("not valid json")

    with patch(
        "simple_NER.annotators.locations_ner.resolve_resource_file",
        side_effect=lambda name: str(bad_json) if name == "countries.json" else None,
    ):
        ner = LocationNER(include_countries=True, include_capitals=True, include_cities=False)
    # Should survive with empty countries list
    assert ner.countries == []


def test_load_vocab_countries_json_not_found():
    """When resolve_resource_file returns None for countries.json, annotator still initialises."""
    from simple_NER.annotators.locations_ner import LocationNER

    with patch(
        "simple_NER.annotators.locations_ner.resolve_resource_file",
        return_value=None,
    ):
        ner = LocationNER(include_countries=True, include_capitals=True, include_cities=False)
    assert ner.countries == []


def test_load_vocab_cities_json_decode_error(tmp_path):
    """OSError/JSONDecodeError on cities.json is caught; annotator still initialises."""
    from simple_NER.annotators.locations_ner import LocationNER

    bad_json = tmp_path / "cities.json"
    bad_json.write_text("not valid json")

    def _resolve(name):
        if name == "cities.json":
            return str(bad_json)
        # Let countries resolve normally so we don't break that path too
        from simple_NER.utils import resolve_resource_file as _real
        return _real(name)

    with patch("simple_NER.annotators.locations_ner.resolve_resource_file", side_effect=_resolve):
        ner = LocationNER(include_countries=False, include_cities=True)
    assert ner.cities == []


def test_load_vocab_cities_json_not_found():
    """When resolve_resource_file returns None for cities.json, annotator still initialises."""
    from simple_NER.annotators.locations_ner import LocationNER

    def _resolve(name):
        if name == "cities.json":
            return None
        from simple_NER.utils import resolve_resource_file as _real
        return _real(name)

    with patch("simple_NER.annotators.locations_ner.resolve_resource_file", side_effect=_resolve):
        ner = LocationNER(include_countries=False, include_cities=True)
    assert ner.cities == []
