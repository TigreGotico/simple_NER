#!/usr/bin/env python3
"""Complete NER pipeline example demonstrating all features.

This example shows how to:
1. Use the annotator factory to create annotators
2. Build a pipeline with multiple annotators
3. Configure deduplication strategies
4. Process text and display results
5. Export results to different formats
"""
from __future__ import annotations

import json
from typing import Any

from simple_NER import Entity
from simple_NER.annotators.factory import (
    create_pipeline,
    get_annotator,
    list_available_annotators,
)
from simple_NER.pipeline import NERPipeline


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" {title} ")
    print("=" * 70)


def print_entity(entity: Entity, show_spans: bool = False) -> None:
    """Print a single entity in a formatted way."""
    spans_str = ""
    if show_spans and entity.spans:
        spans_str = f" spans={entity.spans}"

    data_str = ""
    if entity.data:
        data_items = [f"{k}={v}" for k, v in entity.data.items() if k != "value"]
        if data_items:
            data_str = f" ({', '.join(data_items)})"

    print(
        f"  • {entity.value!r:25} -> {entity.entity_type:20} "
        f"conf={entity.confidence:.2f}{spans_str}{data_str}"
    )


def example_available_annotators() -> None:
    """Show all available annotators."""
    print_header("AVAILABLE ANNOTATORS")

    annotators = list_available_annotators()
    print(f"\nFound {len(annotators)} registered annotators:\n")

    for i, name in enumerate(annotators, 1):
        print(f"  {i:2}. {name}")


def example_single_annotator() -> None:
    """Demonstrate using a single annotator."""
    print_header("SINGLE ANNOTATOR: EMAIL EXTRACTION")

    email_ner = get_annotator("email")
    print(f"Created: {email_ner}\n")

    text = "Contact us at support@example.com or sales@company.org for more info."
    print(f"Text: {text}\n")
    print("Entities found:")

    entities = list(email_ner.extract_entities(text))
    for ent in entities:
        print_entity(ent, show_spans=True)

    print(f"\nTotal: {len(entities)} email(s) detected")


def example_custom_pipeline() -> None:
    """Demonstrate building a custom pipeline."""
    print_header("CUSTOM PIPELINE: EMAIL + NAMES")

    # Create individual annotators
    email_ner = get_annotator("email")
    names_ner = get_annotator("names", confidence=0.7)

    # Build pipeline
    pipeline = NERPipeline(
        annotators=[email_ner, names_ner],
        dedup_strategy="keep_all",
    )

    print(f"Pipeline: {pipeline}\n")

    text = "John Doe and Alice Smith can be reached at john@example.com"
    print(f"Text: {text}\n")
    print("Entities found:")

    entities = pipeline.process(text)
    for ent in entities:
        print_entity(ent)

    print(f"\nTotal: {len(entities)} entity/entities detected")


def example_factory_pipeline() -> None:
    """Demonstrate using the factory to create a pipeline."""
    print_header("FACTORY PIPELINE: MULTIPLE ANNOTATORS")

    # Create pipeline using factory
    try:
        pipeline = create_pipeline(
            annotator_names=["email", "names", "locations"],
            dedup_strategy="keep_higher_confidence",
        )
        print(f"Pipeline: {pipeline}\n")

        text = "John lives in Lisbon and can be contacted at john@test.com"
        print(f"Text: {text}\n")
        print("Entities found:")

        entities = pipeline.process(text)
        for ent in entities:
            print_entity(ent)

        print(f"\nTotal: {len(entities)} entity/entities detected")

    except ValueError as e:
        print(f"Pipeline creation failed (some annotators may not be available): {e}")


def example_deduplication_strategies() -> None:
    """Demonstrate different deduplication strategies."""
    print_header("DEDUPLICATION STRATEGIES")

    # Create a simple pipeline with overlapping detection
    email_ner = get_annotator("email")
    names_ner = get_annotator("names")

    text = "Contact John at john@example.com"

    strategies = ["keep_all", "keep_longest", "keep_higher_confidence", "keep_first"]

    for strategy in strategies:
        pipeline = NERPipeline(
            annotators=[email_ner, names_ner],
            dedup_strategy=strategy,
        )

        entities = pipeline.process(text)
        print(f"\n{strategy}: {len(entities)} entities")
        for ent in entities:
            print(f"  - {ent.value} ({ent.entity_type})")


def example_json_export() -> None:
    """Demonstrate exporting results to JSON."""
    print_header("JSON EXPORT")

    email_ner = get_annotator("email")
    text = "Email us at info@company.com"

    entities = list(email_ner.extract_entities(text))

    # Export to JSON
    json_data = {
        "text": text,
        "entities": [ent.as_json() for ent in entities],
        "count": len(entities),
    }

    print("JSON output:")
    print(json.dumps(json_data, indent=2))


def example_batch_processing() -> None:
    """Demonstrate batch processing of multiple texts."""
    print_header("BATCH PROCESSING")

    email_ner = get_annotator("email")

    texts = [
        "Contact alice@example.com for sales",
        "Support is available at help@company.org",
        "No email in this text",
        "Multiple: one@test.com and two@test.org",
    ]

    print(f"Processing {len(texts)} texts:\n")

    for i, text in enumerate(texts, 1):
        entities = list(email_ner.extract_entities(text))
        print(f"{i}. {text!r}")
        if entities:
            for ent in entities:
                print(f"     → {ent.value}")
        else:
            print("     → No entities found")
        print()


def example_generator_mode() -> None:
    """Demonstrate memory-efficient generator mode."""
    print_header("GENERATOR MODE (MEMORY EFFICIENT)")

    email_ner = get_annotator("email")

    text = "Email: contact@example.com"
    print(f"Text: {text}\n")
    print("Streaming entities:")

    # Use generator instead of list
    for entity in email_ner.extract_entities(text):
        print(f"  [STREAM] {entity.value} -> {entity.entity_type}")


def main() -> None:
    """Run all examples."""
    print_header("SIMPLE_NER COMPLETE PIPELINE EXAMPLE")

    example_available_annotators()
    example_single_annotator()
    example_custom_pipeline()
    example_factory_pipeline()
    example_deduplication_strategies()
    example_json_export()
    example_batch_processing()
    example_generator_mode()

    print_header("ALL EXAMPLES COMPLETED")
    print("\nFor more information, see the documentation:")
    print("  - README.md")
    print("  - CONTRIBUTING.md")
    print("  - examples/ directory\n")


if __name__ == "__main__":
    main()
