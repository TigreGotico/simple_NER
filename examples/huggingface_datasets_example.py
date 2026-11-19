#!/usr/bin/env python
"""Example: Using HuggingFace datasets with simple_NER via ahocorasick-ner.

This example demonstrates how to integrate ahocorasick-ner's HuggingFace
dataset loaders with simple_NER's pipeline architecture for fast,
domain-specific entity extraction.

Requirements:
    pip install "ahocorasick-ner[datasets]"
"""
from ahocorasick_ner.datasets import (
    WikidataEntityNER,
    GenericHFDatasetNER,
    BC5CDRMedicalNER,
)
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline


def example_wikidata_entities():
    """Extract structured entities from Wikidata."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Wikidata Entity Extraction")
    print("=" * 60)

    # Create pipeline
    pipeline = NERPipeline(dedup_strategy="keep_longest")

    # Add animals from Wikidata
    print("\nLoading animals from Wikidata (Q729)...")
    animals = WikidataEntityNER(entity_type="Animal", wikidata_qid="Q729")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(animals))

    # Add countries from Wikidata
    print("Loading countries from Wikidata (Q6256)...")
    countries = WikidataEntityNER(entity_type="Country", wikidata_qid="Q6256")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(countries))

    # Test
    text = "A dog from Japan and a cat from France met in Berlin"
    print(f"\nInput: {text}")
    print("\nExtracted entities:")
    for entity in pipeline.process(text):
        print(f"  {entity.entity_type:12} → {entity.value}")


def example_generic_dataset():
    """Extract entities from any HuggingFace dataset with a name column."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Generic HuggingFace Dataset")
    print("=" * 60)

    pipeline = NERPipeline()

    # Load colors from the color-pedia dataset
    print("\nLoading colors from boltuix/color-pedia...")
    colors = GenericHFDatasetNER(
        entity_type="Color",
        hf_dataset="boltuix/color-pedia",
        column="name",
    )
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(colors))

    # Test
    text = "The red car drove past the blue house under a gray sky"
    print(f"\nInput: {text}")
    print("\nExtracted colors:")
    for entity in pipeline.process(text):
        print(f"  {entity.value}")


def example_biomedical():
    """Extract diseases and chemicals from biomedical text."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Biomedical Entity Extraction (BC5CDR)")
    print("=" * 60)

    pipeline = NERPipeline()

    # Load diseases
    print("\nLoading diseases from BC5CDR...")
    diseases = BC5CDRMedicalNER(entity_type="Disease")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(diseases))

    # Load chemicals
    print("Loading chemicals from BC5CDR...")
    chemicals = BC5CDRMedicalNER(entity_type="Chemical")
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(chemicals))

    # Test
    text = (
        "Aspirin can help treat headaches and migraines. "
        "Patients with arthritis may benefit from NSAIDs."
    )
    print(f"\nInput: {text}")
    print("\nExtracted biomedical entities:")
    for entity in pipeline.process(text):
        print(f"  {entity.entity_type:12} → {entity.value}")


def example_auto_qid_mapping():
    """Use WikidataEntityNER with auto QID mapping by entity type name."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Auto QID Mapping")
    print("=" * 60)

    print("\nAvailable entity types for auto-mapping:")
    print("  ", list(WikidataEntityNER.QIDS.keys()))

    # Create without specifying wikidata_qid—it auto-maps from entity_type
    print("\nLoading professions from Wikidata (auto-mapped)...")
    professions = WikidataEntityNER(entity_type="Profession")
    pipeline = NERPipeline()
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(professions))

    text = "Alice is a doctor, Bob works as an engineer, and Charlie is a lawyer"
    print(f"\nInput: {text}")
    print("\nExtracted professions:")
    for entity in pipeline.process(text):
        print(f"  {entity.value}")


def example_media_entities():
    """Extract media-related entities (actors, directors, bands, etc.)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Media Entities (Entertainment & Music)")
    print("=" * 60)

    from ahocorasick_ner.datasets import (
        MovieActorNER,
        MovieDirectorNER,
        JazzNER,
        MetalArchivesBandsNER,
    )

    pipeline = NERPipeline()

    # Add movie actors
    print("\nLoading movie actors (6.3M from IMDB)...")
    actors = MovieActorNER()
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(actors))

    # Add directors
    print("Loading movie directors (128k from IMDB)...")
    directors = MovieDirectorNER()
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(directors))

    text = (
        "A film by Steven Spielberg starred Tom Hanks and Meryl Streep. "
        "It won an Oscar for Best Picture."
    )
    print(f"\nInput: {text}")
    print("\nExtracted movie entities:")
    for entity in pipeline.process(text):
        print(f"  {entity.entity_type:20} → {entity.value}")


def example_music_entities():
    """Extract music artist and band names."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Music Entities (Bands, Artists, Genres)")
    print("=" * 60)

    from ahocorasick_ner.datasets import JazzNER, MetalArchivesBandsNER

    pipeline = NERPipeline()

    # Add metal bands
    print("\nLoading metal bands from Encyclopedia Metallum...")
    bands = MetalArchivesBandsNER()
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(bands))

    # Add jazz artists
    print("Loading jazz artists and genres...")
    jazz = JazzNER()
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(jazz))

    text = (
        "Black Sabbath was a heavy metal band, "
        "while Miles Davis pioneered cool jazz."
    )
    print(f"\nInput: {text}")
    print("\nExtracted music entities:")
    for entity in pipeline.process(text):
        print(f"  {entity.entity_type:20} → {entity.value}")


if __name__ == "__main__":
    print("\n🚀 simple_NER + ahocorasick-ner HuggingFace Dataset Examples\n")

    try:
        example_wikidata_entities()
    except Exception as e:
        print(f"⚠️  Wikidata example skipped: {e}")

    try:
        example_generic_dataset()
    except Exception as e:
        print(f"⚠️  Generic dataset example skipped: {e}")

    try:
        example_biomedical()
    except Exception as e:
        print(f"⚠️  Biomedical example skipped: {e}")

    try:
        example_auto_qid_mapping()
    except Exception as e:
        print(f"⚠️  Auto QID example skipped: {e}")

    try:
        example_media_entities()
    except Exception as e:
        print(f"⚠️  Media entities example skipped: {e}")

    try:
        example_music_entities()
    except Exception as e:
        print(f"⚠️  Music entities example skipped: {e}")

    print("\n✅ Examples completed!\n")
