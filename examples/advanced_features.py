#!/usr/bin/env python3
"""Advanced examples demonstrating streaming, async, and visualization features.

This example shows:
1. Streaming text processing
2. Async pipeline execution
3. Caching results
4. Batch processing
5. Entity visualization
"""
from __future__ import annotations

import asyncio
import time


def example_streaming() -> None:
    """Demonstrate streaming text processing."""
    from simple_NER.annotators.email_ner import EmailAnnotator
    from simple_NER.pipeline import NERPipeline
    from simple_NER.utils.batch import StreamingProcessor

    print("\n" + "=" * 70)
    print("STREAMING PROCESSING")
    print("=" * 70)

    # Create pipeline
    pipeline = NERPipeline([EmailAnnotator()])
    processor = StreamingProcessor(pipeline, buffer_size=3)

    # Simulate streaming input
    def text_stream():
        texts = [
            "Contact john@example.com for sales",
            "Support: help@company.org",
            "No email here",
            "Multiple: one@test.com and two@test.org",
            "Final email: last@example.com",
        ]
        for text in texts:
            yield text

    print("Processing stream:")
    for text, entities in processor.process_stream(text_stream()):
        print(f"  {text!r} -> {len(entities)} entities")
        for ent in entities:
            print(f"    - {ent.value}")


def example_caching() -> None:
    """Demonstrate result caching."""
    from simple_NER.annotators.email_ner import EmailAnnotator
    from simple_NER.pipeline import NERPipeline
    from simple_NER.utils.cache import LRUCache

    print("\n" + "=" * 70)
    print("CACHING")
    print("=" * 70)

    pipeline = NERPipeline([EmailAnnotator()])
    cache = LRUCache(max_size=10)

    texts = [
        "Contact john@example.com",
        "Email: test@company.org",
        "Contact john@example.com",  # Duplicate
        "Email: test@company.org",   # Duplicate
        "New: unique@email.com",
    ]

    print("Processing with cache:")
    for text in texts:
        # Check cache first
        cached = cache.get(text)
        if cached is not None:
            print(f"  [CACHE HIT] {text!r} -> {len(cached)} entities")
        else:
            entities = pipeline.process(text)
            cache.set(text, entities)
            print(f"  [CACHE MISS] {text!r} -> {len(entities)} entities")

    print(f"\nCache stats: {cache.stats()}")


async def example_async() -> None:
    """Demonstrate async pipeline execution."""
    from simple_NER.annotators.email_ner import EmailAnnotator
    from simple_NER.annotators.names_ner import NamesNER
    from simple_NER.pipeline import AsyncNERPipeline

    print("\n" + "=" * 70)
    print("ASYNC PROCESSING")
    print("=" * 70)

    # Create async pipeline
    pipeline = AsyncNERPipeline([EmailAnnotator(), NamesNER()])

    texts = [
        "John Doe at john@example.com",
        "Alice Smith, alice@test.org",
        "Bob Johnson, bob@company.com",
    ]

    # Process single text
    print("Single text:")
    start = time.perf_counter()
    entities = await pipeline.process_async(texts[0])
    elapsed = time.perf_counter() - start
    print(f"  {texts[0]!r} -> {len(entities)} entities ({elapsed*1000:.2f}ms)")

    # Process batch
    print("\nBatch processing:")
    start = time.perf_counter()
    results = await pipeline.process_batch_async(texts, max_concurrency=2)
    elapsed = time.perf_counter() - start

    for text, entities in zip(texts, results):
        print(f"  {text!r} -> {len(entities)} entities")
    print(f"Total time: {elapsed*1000:.2f}ms")


def example_visualization() -> None:
    """Demonstrate entity visualization."""
    from simple_NER.annotators.email_ner import EmailAnnotator
    from simple_NER.annotators.names_ner import NamesNER
    from simple_NER.pipeline import NERPipeline
    from simple_NER.utils.visualization import (
        print_colored_entities,
        visualize_entities_table,
        visualize_text_html,
        visualize_text_terminal,
    )

    print("\n" + "=" * 70)
    print("VISUALIZATION")
    print("=" * 70)

    pipeline = NERPipeline([EmailAnnotator(), NamesNER()])
    text = "John Doe lives in Lisbon. Contact: john@example.com"

    entities = pipeline.process(text)

    # Terminal visualization
    print("\nTerminal visualization:")
    print(visualize_text_terminal(text, entities, show_confidence=True))

    # Table visualization
    print("\nTable visualization:")
    print(visualize_entities_table(entities))

    # HTML visualization
    print("\nHTML visualization:")
    html = visualize_text_html(text, entities)
    print(f"  {html[:100]}...")

    # Colored print
    print("\nColored entities:")
    print_colored_entities(entities)


def example_batch_processing() -> None:
    """Demonstrate batch processing with progress."""
    from simple_NER.annotators.email_ner import EmailAnnotator
    from simple_NER.pipeline import NERPipeline
    from simple_NER.utils.batch import BatchProcessor

    print("\n" + "=" * 70)
    print("BATCH PROCESSING")
    print("=" * 70)

    pipeline = NERPipeline([EmailAnnotator()])
    processor = BatchProcessor(pipeline, batch_size=5)

    # Generate sample texts
    texts = [f"Email: user{i}@example.com" for i in range(20)]

    def progress_callback(current: int, total: int) -> None:
        percent = (current / total) * 100
        print(f"  Progress: {current}/{total} ({percent:.1f}%)")

    print("Processing batch:")
    results = processor.process_batch(
        texts,
        use_multiprocessing=False,
        progress_callback=progress_callback,
    )

    total_entities = sum(len(r) for r in results)
    print(f"\nProcessed {len(texts)} texts, found {total_entities} entities")


def main() -> None:
    """Run all advanced examples."""
    print("=" * 70)
    print(" SIMPLE_NER ADVANCED EXAMPLES ")
    print("=" * 70)

    example_streaming()
    example_caching()

    # Async requires event loop
    asyncio.run(example_async())

    example_visualization()
    example_batch_processing()

    print("\n" + "=" * 70)
    print(" ALL EXAMPLES COMPLETED ")
    print("=" * 70)


if __name__ == "__main__":
    main()
