"""Location entity extraction (countries, capitals, and cities).

This module provides extraction of geographical entities including:
- Countries (Portugal, United States, Japan)
- Country codes (PT, US, JP)
- Capital cities (Lisbon, Washington, Tokyo)
- Cities (Porto, New York, Osaka)
"""
from __future__ import annotations

import json
from collections.abc import Generator
from typing import Any

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.utils import resolve_resource_file
from simple_NER.utils.log import LOG

from ahocorasick_ner import AhocorasickNER as _AhocorasickNER


class LocationNER(BaseAnnotator):
    """Extract location entities from text.

    Language support: language-agnostic (JSON vocabulary lookup on proper names).
    Matching is case-sensitive by default; pass ``lowercase=True`` to disable.

    This annotator combines country, country code, capital city, and city
    extraction in a single class, as they share common infrastructure
    (JSON vocabularies, word matching).

    Attributes:
        lowercase: Enable case-insensitive matching.
        include_countries: Extract country names and codes.
        include_capitals: Extract capital cities.
        include_cities: Extract all cities.

    Example:
        ```python
        from simple_NER.annotators.locations_ner import LocationNER

        ner = LocationNER()
        for ent in ner.extract_entities("Lisbon is the capital of Portugal"):
            print(f"{ent.value} -> {ent.entity_type}")
            # "Lisbon" -> Capital City
            # "Portugal" -> Country
        ```
    """

    def __init__(
        self,
        lowercase: bool = False,
        include_countries: bool = True,
        include_capitals: bool = True,
        include_cities: bool = True,
        confidence: float = 0.9,
    ) -> None:
        """Initialize location NER.

        Args:
            lowercase: Enable case-insensitive matching.
            include_countries: Extract country names and codes.
            include_capitals: Extract capital cities.
            include_cities: Extract all cities.
            confidence: Default confidence score for entities.
                Reduced to 0.75 when lowercase=True.
        """
        self.lowercase = lowercase
        self._include_countries = include_countries
        self._include_capitals = include_capitals
        self._include_cities = include_cities

        # Adjust confidence for case-insensitive matching
        base_confidence = confidence if not lowercase else 0.75
        super().__init__(confidence=base_confidence)

        self._countries: list[dict[str, Any]] = []
        self._cities: list[dict[str, Any]] = []
        # Keyed by "<label>|<canonical_name>" → entity data dict
        self._meta: dict[str, dict[str, Any]] = {}
        self._ac: Any = None  # AhocorasickNER or None
        self._load_vocab()
        self._build_automaton()

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "location"

    def _load_vocab(self) -> None:
        """Load country and city vocabularies from JSON files."""
        if self._include_countries or self._include_capitals:
            countries_file = resolve_resource_file("countries.json")
            if countries_file:
                try:
                    with open(countries_file) as f:
                        self._countries = json.load(f)
                    self._process_countries()
                except (OSError, json.JSONDecodeError) as e:
                    LOG.error(f"Failed to load countries.json: {e}")
            else:
                LOG.warning("countries.json not found")

        if self._include_cities:
            cities_file = resolve_resource_file("cities.json")
            if cities_file:
                try:
                    with open(cities_file) as f:
                        self._cities = json.load(f)
                except (OSError, json.JSONDecodeError) as e:
                    LOG.error(f"Failed to load cities.json: {e}")
            else:
                LOG.warning("cities.json not found")

    def _process_countries(self) -> None:
        """Normalise country data (latlng → latitude/longitude, hemisphere)."""
        for country in self._countries:
            if "latlng" in country and "latitude" not in country:
                lat, lon = country.pop("latlng")
                country["latitude"] = lat
                country["longitude"] = lon
            if "latitude" in country:
                country["hemisphere"] = "south" if country["latitude"] < 0 else "north"

    def _build_automaton(self) -> None:
        """Build Aho-Corasick automaton from loaded vocabularies.

        Each entry is registered as ``label|canonical_name`` so ``_meta``
        can recover full entity data from an AC match without a second lookup.
        Falls back to the legacy word-scan when ``ahocorasick-ner`` is absent.
        """
        self._meta.clear()

        def _add(ac: Any, label: str, surface: str, data: dict[str, Any]) -> None:
            if not surface:
                return
            key = f"{label}|{surface}"
            self._meta[key] = data
            ac.add_word(label, surface)

        ac = _AhocorasickNER(case_sensitive=not self.lowercase)

        if self._include_countries or self._include_capitals:
            for country in self._countries:
                name = country["name"]
                code = country.get("country_code", "")
                capital = country.get("capital", "")
                data = country.copy()

                if self._include_countries:
                    _add(ac, "Country", name, data)
                    if code:
                        _add(ac, "Country_code", code, data)
                if self._include_capitals and capital:
                    cap_data = {
                        "country_name": name,
                        "country_code": code,
                        "name": capital,
                        "hemisphere": country.get("hemisphere", "north"),
                    }
                    _add(ac, "Capital City", capital, cap_data)

        if self._include_cities:
            for city in self._cities:
                city_name = city["name"]
                lat = float(city.get("lat", 0))
                lng = float(city.get("lng", 0))
                city_data = {
                    "name": city_name,
                    "country_code": city.get("country", ""),
                    "latitude": lat,
                    "longitude": lng,
                    "hemisphere": "south" if lat < 0 else "north",
                }
                _add(ac, "City", city_name, city_data)

        ac.fit()
        self._ac = ac
        total = sum(1 for k in self._meta)
        LOG.debug(f"LocationNER: Aho-Corasick automaton built with {total} patterns")

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract location entities from text.

        Uses Aho-Corasick for O(N) phrase matching — correctly detects
        multi-word names like "New York" or "United States".

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for countries, capitals, and cities.
        """
        for match in self._ac.tag(text, min_word_len=1):
            key = f"{match['label']}|{match['word']}"
            meta = self._meta.get(key)
            if meta is None:
                continue
            yield Entity(
                match["word"],
                match["label"],
                source_text=text,
                data={**meta, "start": match["start"], "end": match["end"]},
                confidence=self.confidence,
            )

    @property
    def countries(self) -> list[dict[str, Any]]:
        """Return loaded country data."""
        return self._countries

    @property
    def cities(self) -> list[dict[str, Any]]:
        """Return loaded city data."""
        return self._cities


# Backward compatibility aliases
CitiesNER = LocationNER


if __name__ == "__main__":
    from pprint import pprint

    print("=" * 60)
    print("COUNTRY AND CAPITAL EXTRACTION")
    print("=" * 60)

    ner = LocationNER()
    text = "The capital of Portugal is Lisbon"
    for r in ner.extract_entities(text):
        print(f"{r.value} - {r.entity_type}")
        pprint(r.as_json())

    print("\n" + "=" * 60)
    print("CITY EXTRACTION ONLY")
    print("=" * 60)

    ner_cities = LocationNER(
        include_countries=False, include_capitals=False, include_cities=True
    )
    text = "Portugal was born in Guimarães"
    for r in ner_cities.extract_entities(text):
        print(f"{r.value} - {r.entity_type}")
        pprint(r.as_json())
