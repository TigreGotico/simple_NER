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
        self._load_vocab()

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
        """Pre-process country data for efficient lookup."""
        for country in self._countries:
            if "latlng" in country and "latitude" not in country:
                lat, lon = country.pop("latlng")
                country["latitude"] = lat
                country["longitude"] = lon

            if "latitude" in country:
                country["hemisphere"] = (
                    "south" if country["latitude"] < 0 else "north"
                )

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract location entities from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for countries, capitals, and cities.
        """
        if self.lowercase:
            words = text.lower().split()
        else:
            words = text.split()

        # Extract countries and capitals
        if self._include_countries or self._include_capitals:
            yield from self._extract_countries(words, text)

        # Extract cities
        if self._include_cities:
            yield from self._extract_cities(words, text)

    def _extract_countries(
        self, words: list[str], text: str
    ) -> Generator[Entity, None, None]:
        """Extract country and capital entities.

        Args:
            words: Tokenized text.
            text: Original text for source_text.

        Yields:
            Entity objects for countries and capitals.
        """
        for word in words:
            for country in self._countries:
                name = country["name"]
                code = country.get("country_code", "")
                capital = country.get("capital", "")

                if self.lowercase:
                    name = name.lower()
                    code = code.lower() if code else ""
                    capital = capital.lower() if capital else ""

                if word == name and self._include_countries:
                    yield Entity(
                        country["name"],
                        "Country",
                        source_text=text,
                        data=country.copy(),
                        confidence=self.confidence,
                    )
                elif word == code and code and self._include_countries:
                    yield Entity(
                        code,
                        "Country_code",
                        source_text=text,
                        data=country.copy(),
                        confidence=self.confidence,
                    )
                elif word == capital and capital and self._include_capitals:
                    data = {
                        "country_name": country["name"],
                        "country_code": country.get("country_code", ""),
                        "name": capital,
                        "hemisphere": country.get("hemisphere", "north"),
                    }
                    yield Entity(
                        capital,
                        "Capital City",
                        source_text=text,
                        data=data,
                        confidence=self.confidence,
                    )

    def _extract_cities(
        self, words: list[str], text: str
    ) -> Generator[Entity, None, None]:
        """Extract city entities.

        Args:
            words: Tokenized text.
            text: Original text for source_text.

        Yields:
            Entity objects for cities.
        """
        for word in words:
            for city in self._cities:
                name = city["name"]
                code = city.get("country", "")
                lat = float(city.get("lat", 0))
                lng = float(city.get("lng", 0))

                if self.lowercase:
                    name = name.lower()

                if word == name:
                    data = {
                        "name": city["name"],
                        "country_code": code,
                        "latitude": lat,
                        "longitude": lng,
                        "hemisphere": "south" if lat < 0 else "north",
                    }
                    yield Entity(
                        city["name"],
                        "City",
                        source_text=text,
                        data=data,
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
