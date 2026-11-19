#!/usr/bin/env python
"""Example: Comprehensive dataset integration showcase.

Demonstrates all major dataset loaders including business, music, food,
programming, and extended Wikidata categories.

Requirements:
    pip install simple_NER "ahocorasick-ner[datasets]"
"""
from ahocorasick_ner.datasets import (
    # Business
    CompanyNamesNER,
    # Music
    SpotifyTracksNER,
    # Food
    RecipeIngredientsNER,
    FoodProductsNER,
    # Programming
    ProgrammingLanguageNER,
    # Wikidata Extended
    WikidataLandmarkNER,
    WikidataUniversityNER,
    WikidataMovieNER,
    WikidataAuthorNER,
    WikidataAthleteNER,
    WikidataSportsTeamNER,
)
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline


def example_business_and_commerce():
    """Extract company names and brands."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Business & E-Commerce")
    print("=" * 70)

    pipeline = NERPipeline()
    print("Loading company names (50k+)...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(CompanyNamesNER()))

    text = "Apple and Microsoft compete with Google in the tech industry"
    print(f"\nInput: {text}")
    print("\nCompanies found:")
    for entity in pipeline.process(text):
        print(f"  - {entity.value}")


def example_music_and_entertainment():
    """Extract music entities: tracks, artists, genres."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Music & Entertainment")
    print("=" * 70)

    pipeline = NERPipeline()
    print("Loading Spotify tracks (200k+)...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(SpotifyTracksNER()))

    text = (
        "Bohemian Rhapsody by Queen is a rock classic. "
        "Blinding Lights by The Weeknd is electropop."
    )
    print(f"\nInput: {text}")
    print("\nMusic entities found:")

    by_type = {}
    for entity in pipeline.process(text):
        if entity.entity_type not in by_type:
            by_type[entity.entity_type] = []
        by_type[entity.entity_type].append(entity.value)

    for etype, values in sorted(by_type.items()):
        print(f"  {etype:15} → {', '.join(values)}")


def example_food_and_cooking():
    """Extract recipe ingredients and food products."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Food & Recipes")
    print("=" * 70)

    pipeline = NERPipeline()
    print("Loading recipe ingredients (2.2M recipes)...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(RecipeIngredientsNER()))
    print("Loading food products (4M+)...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(FoodProductsNER()))

    text = (
        "Mix flour, butter, and eggs. Add Coca-Cola and Lay's potato chips. "
        "Top with sugar and vanilla extract."
    )
    print(f"\nInput: {text}")
    print("\nFood entities found:")

    by_type = {}
    for entity in pipeline.process(text):
        if entity.entity_type not in by_type:
            by_type[entity.entity_type] = []
        by_type[entity.entity_type].append(entity.value)

    for etype, values in sorted(by_type.items()):
        print(f"  {etype:15} → {', '.join(values)}")


def example_programming_and_tech():
    """Extract programming language names."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Programming & Technology")
    print("=" * 70)

    pipeline = NERPipeline()
    print("Loading programming languages (50+)...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(ProgrammingLanguageNER()))

    text = (
        "Popular languages: Python, JavaScript, Java, Go, Rust, TypeScript. "
        "For systems: C++, C#, Swift. Emerging: Kotlin, Zig."
    )
    print(f"\nInput: {text}")
    print("\nProgramming languages found:")
    for entity in pipeline.process(text):
        print(f"  - {entity.value}")


def example_wikidata_extended():
    """Extract various Wikidata entities."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Extended Wikidata Categories")
    print("=" * 70)

    # Books & Authors
    print("\n--- Books & Authors ---")
    pipeline = NERPipeline()
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAuthorNER()))

    text = "J.K. Rowling and Stephen King are famous authors"
    print(f"Input: {text}")
    for entity in pipeline.process(text):
        print(f"  Author: {entity.value}")

    # Sports
    print("\n--- Sports ---")
    pipeline = NERPipeline()
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAthleteNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataSportsTeamNER()))

    text = "Lionel Messi and Cristiano Ronaldo played for Barcelona and Manchester"
    print(f"Input: {text}")
    for entity in pipeline.process(text):
        print(f"  {entity.entity_type:15} → {entity.value}")

    # Landmarks & Culture
    print("\n--- Landmarks & Culture ---")
    pipeline = NERPipeline()
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataLandmarkNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataUniversityNER()))

    text = (
        "Visit the Eiffel Tower and Statue of Liberty. "
        "Study at Harvard University or MIT."
    )
    print(f"Input: {text}")
    for entity in pipeline.process(text):
        print(f"  {entity.entity_type:15} → {entity.value}")

    # Movies
    print("\n--- Movies ---")
    pipeline = NERPipeline()
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataMovieNER()))

    text = "Avatar and Inception are groundbreaking films"
    print(f"Input: {text}")
    for entity in pipeline.process(text):
        print(f"  Movie: {entity.value}")


def example_comprehensive():
    """Combine many datasets for comprehensive extraction."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Comprehensive Multi-Domain Extraction")
    print("=" * 70)

    pipeline = NERPipeline(dedup_strategy="keep_longest")

    print("Loading 10 datasets...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(CompanyNamesNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(SpotifyTracksNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(RecipeIngredientsNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(ProgrammingLanguageNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAuthorNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataMovieNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataLandmarkNER()))

    text = (
        "Microsoft funded a research project at Harvard University "
        "using Python and JavaScript. They watched Avatar on Netflix "
        "with Queen songs playing. The recipe used flour and butter."
    )

    print(f"\nInput: {text[:80]}...")
    print("\nExtracted entities (by type):")

    by_type = {}
    for entity in pipeline.process(text):
        if entity.entity_type not in by_type:
            by_type[entity.entity_type] = []
        by_type[entity.entity_type].append(entity.value)

    for etype in sorted(by_type.keys()):
        values = by_type[etype]
        print(f"  {etype:20} → {', '.join(values)}")


if __name__ == "__main__":
    print("\n🚀 Comprehensive Dataset Integration Examples\n")

    try:
        example_business_and_commerce()
    except Exception as e:
        print(f"⚠️  Example 1 skipped: {e}")

    try:
        example_music_and_entertainment()
    except Exception as e:
        print(f"⚠️  Example 2 skipped: {e}")

    try:
        example_food_and_cooking()
    except Exception as e:
        print(f"⚠️  Example 3 skipped: {e}")

    try:
        example_programming_and_tech()
    except Exception as e:
        print(f"⚠️  Example 4 skipped: {e}")

    try:
        example_wikidata_extended()
    except Exception as e:
        print(f"⚠️  Example 5 skipped: {e}")

    try:
        example_comprehensive()
    except Exception as e:
        print(f"⚠️  Example 6 skipped: {e}")

    print("\n✅ Examples completed!\n")
