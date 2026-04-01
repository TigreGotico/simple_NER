#!/usr/bin/env python
"""Example: Dedicated Wikidata subclasses for easy entity extraction.

Shows how much simpler it is to use the dedicated subclasses compared to
the generic WikidataEntityNER with manual QID specification.

Requirements:
    pip install "ahocorasick-ner[datasets]"
"""
from ahocorasick_ner.datasets import (
    WikidataAnimalNER,
    WikidataCountryNER,
    WikidataPersonNER,
    WikidataProfessionNER,
    WikidataDiseaseNER,
    WikidataPlantNER,
    GeoNamesNER,
    PersonNamesNER,
)
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline


def example_easy_wikidata_subclasses():
    """Use dedicated Wikidata subclasses for clean, discoverable code."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Easy Wikidata Subclasses (No QID Required)")
    print("=" * 70)

    print("\n# OLD WAY (requires knowing Wikidata QIDs):")
    print("  from ahocorasick_ner.datasets import WikidataEntityNER")
    print("  animals = WikidataEntityNER(entity_type='Animal', wikidata_qid='Q729')")
    print("  countries = WikidataEntityNER(entity_type='Country', wikidata_qid='Q6256')")

    print("\n# NEW WAY (simple and discoverable):")
    print("  from ahocorasick_ner.datasets import WikidataAnimalNER, WikidataCountryNER")
    print("  animals = WikidataAnimalNER()")
    print("  countries = WikidataCountryNER()")

    print("\n" + "-" * 70)
    print("Creating pipeline with multiple Wikidata entities...")
    print("-" * 70)

    pipeline = NERPipeline(dedup_strategy="keep_longest")

    # Add multiple entity types — just name the class, no QID needed
    print("Adding: Animals, Countries, Professions, Diseases...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAnimalNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataCountryNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataProfessionNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataDiseaseNER()))

    text = (
        "In Japan, a doctor treats patients with arthritis. "
        "A dog is a popular pet in many countries."
    )
    print(f"\nInput: {text}")
    print("\nExtracted entities:")
    for entity in pipeline.process(text):
        print(f"  {entity.entity_type:15} → {entity.value}")


def example_multilingual_wikidata():
    """Wikidata subclasses support multiple languages."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multilingual Wikidata Entity Extraction")
    print("=" * 70)

    print("\nExtracting animals in different languages...\n")

    # English
    print("ENGLISH (en-us):")
    animals_en = WikidataAnimalNER(lang="en-us")
    pipeline_en = NERPipeline()
    pipeline_en.add_annotator(AhocorasickAnnotatorWrapper(animals_en))
    for entity in pipeline_en.process("Dogs, cats, and eagles are animals"):
        print(f"  {entity.value}")

    # German
    print("\nGERMAN (de-de):")
    animals_de = WikidataAnimalNER(lang="de-de")
    pipeline_de = NERPipeline()
    pipeline_de.add_annotator(AhocorasickAnnotatorWrapper(animals_de))
    for entity in pipeline_de.process("Hunde, Katzen und Adler sind Tiere"):
        print(f"  {entity.value}")

    # Spanish
    print("\nSPANISH (es):")
    animals_es = WikidataAnimalNER(lang="es")
    pipeline_es = NERPipeline()
    pipeline_es.add_annotator(AhocorasickAnnotatorWrapper(animals_es))
    for entity in pipeline_es.process("Perros, gatos y águilas son animales"):
        print(f"  {entity.value}")


def example_locations_and_names():
    """Extract locations and person names."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Locations (GeoNames) & Person Names")
    print("=" * 70)

    pipeline = NERPipeline()

    print("\nLoading GeoNames locations (280k+ cities)...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(GeoNamesNER()))

    print("Loading person surnames (30+ countries)...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(PersonNamesNER()))

    text = (
        "John Smith visited Paris. Maria Garcia traveled to Tokyo. "
        "James Murphy met friends in London."
    )
    print(f"\nInput: {text}")
    print("\nExtracted entities:")
    for entity in pipeline.process(text):
        print(f"  {entity.entity_type:15} → {entity.value}")


def example_comprehensive():
    """Comprehensive example with all entity types."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Comprehensive Entity Extraction")
    print("=" * 70)

    pipeline = NERPipeline(dedup_strategy="keep_longest")

    print("Loading 10 entity types from Wikidata + Locations + Names...")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAnimalNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataPlantNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataCountryNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataPersonNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataProfessionNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataDiseaseNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(GeoNamesNER()))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(PersonNamesNER()))

    text = (
        "Dr. Smith, a physician in Paris, owns a dog named Max. "
        "He travels to Japan where he studies roses and treats patients with arthritis. "
        "His colleague Maria Garcia works there too."
    )
    print(f"\nInput: {text}")
    print("\nExtracted entities (by type):")

    by_type = {}
    for entity in pipeline.process(text):
        if entity.entity_type not in by_type:
            by_type[entity.entity_type] = []
        by_type[entity.entity_type].append(entity.value)

    for entity_type in sorted(by_type.keys()):
        values = by_type[entity_type]
        print(f"  {entity_type:15} → {', '.join(values)}")


if __name__ == "__main__":
    print("\n🚀 Wikidata Subclasses & Multilingual Entity Extraction\n")

    try:
        example_easy_wikidata_subclasses()
    except Exception as e:
        print(f"⚠️  Example 1 skipped: {e}")

    try:
        example_multilingual_wikidata()
    except Exception as e:
        print(f"⚠️  Example 2 skipped: {e}")

    try:
        example_locations_and_names()
    except Exception as e:
        print(f"⚠️  Example 3 skipped: {e}")

    try:
        example_comprehensive()
    except Exception as e:
        print(f"⚠️  Example 4 skipped: {e}")

    print("\n✅ Examples completed!\n")
