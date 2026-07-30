#!/usr/bin/env python3
"""Benchmark script for simple_NER performance testing.

This script measures:
- Extraction speed for different annotators
- Memory usage
- Pipeline performance
- Comparison of deduplication strategies

Usage:
    python -m simple_NER.benchmark
    python -m simple_NER.benchmark --annotators email,names
    python -m simple_NER.benchmark --text "custom text"
    python -m simple_NER.benchmark --iterations 100
"""
from __future__ import annotations

import argparse
import time

from simple_NER.annotators.base import BaseAnnotator
from simple_NER.annotators.factory import get_annotator, list_available_annotators
from simple_NER.pipeline import NERPipeline

# Sample texts for benchmarking
SAMPLE_TEXTS = {
    "short": "Contact john@example.com for more info",
    "medium": (
        "John Doe lives in Lisbon and works at Tech Corp. "
        "Contact him at john.doe@techcorp.com or call 555-123-4567. "
        "The meeting is scheduled for tomorrow at 3pm."
    ),
    "long": (
        "Dr. Alice Smith, a researcher at MIT in Cambridge, Massachusetts, "
        "published a groundbreaking study on machine learning. "
        "The study analyzed over 10,000 data points spanning five years. "
        "Contact: alice.smith@mit.edu. The research was funded by a $2.5M grant "
        "from the National Science Foundation. Results show a 35% improvement "
        "in accuracy compared to previous methods. The findings were presented "
        "at the International Conference on AI in Paris last month."
    ),
}


class BenchmarkResult:
    """Store benchmark results."""

    def __init__(self, name: str, iterations: int) -> None:
        self.name = name
        self.iterations = iterations
        self.total_time: float = 0.0
        self.avg_time: float = 0.0
        self.min_time: float = float("inf")
        self.max_time: float = 0.0
        self.entities_found: int = 0
        self.entities_per_second: float = 0.0

    def add_run(self, elapsed: float, entities: int) -> None:
        """Add a single run result."""
        self.total_time += elapsed
        self.entities_found += entities
        self.min_time = min(self.min_time, elapsed)
        self.max_time = max(self.max_time, elapsed)

    def finalize(self) -> None:
        """Calculate averages and rates."""
        if self.iterations > 0:
            self.avg_time = self.total_time / self.iterations
            if self.total_time > 0:
                self.entities_per_second = self.entities_found / self.total_time

    def __str__(self) -> str:
        return (
            f"{self.name:25} | "
            f"avg: {self.avg_time*1000:7.2f}ms | "
            f"min: {self.min_time*1000:7.2f}ms | "
            f"max: {self.max_time*1000:7.2f}ms | "
            f"entities: {self.entities_found:4} | "
            f"rate: {self.entities_per_second:6.1f}/s"
        )


def time_annotator(
    annotator: BaseAnnotator, text: str, iterations: int
) -> BenchmarkResult:
    """Benchmark a single annotator.

    Args:
        annotator: Annotator to benchmark.
        text: Text to process.
        iterations: Number of iterations.

    Returns:
        BenchmarkResult with timing information.
    """
    result = BenchmarkResult(annotator.name, iterations)

    for _ in range(iterations):
        start = time.perf_counter()
        entities = list(annotator.extract_entities(text))
        elapsed = time.perf_counter() - start

        result.add_run(elapsed, len(entities))

    result.finalize()
    return result


def time_pipeline(
    pipeline: NERPipeline, text: str, iterations: int
) -> BenchmarkResult:
    """Benchmark a pipeline.

    Args:
        pipeline: Pipeline to benchmark.
        text: Text to process.
        iterations: Number of iterations.

    Returns:
        BenchmarkResult with timing information.
    """
    result = BenchmarkResult(str(pipeline), iterations)

    for _ in range(iterations):
        start = time.perf_counter()
        entities = pipeline.process(text)
        elapsed = time.perf_counter() - start

        result.add_run(elapsed, len(entities))

    result.finalize()
    return result


def benchmark_single_annotators(
    annotator_names: list[str], text: str, iterations: int
) -> list[BenchmarkResult]:
    """Benchmark individual annotators.

    Args:
        annotator_names: List of annotator names to test.
        text: Text to process.
        iterations: Number of iterations.

    Returns:
        List of BenchmarkResult objects.
    """
    results = []

    print(f"\nBenchmarking {len(annotator_names)} annotator(s)...")
    print("-" * 90)

    for name in annotator_names:
        try:
            annotator = get_annotator(name)
            result = time_annotator(annotator, text, iterations)
            results.append(result)
            print(result)
        except Exception as e:
            print(f"{name:25} | SKIPPED: {e}")

    return results


def benchmark_dedup_strategies(
    annotator_names: list[str], text: str, iterations: int
) -> None:
    """Benchmark different deduplication strategies.

    Args:
        annotator_names: List of annotator names to use.
        text: Text to process.
        iterations: Number of iterations.
    """
    strategies = ["keep_all", "keep_longest", "keep_higher_confidence", "keep_first"]

    print("\nBenchmarking deduplication strategies...")
    print("-" * 90)

    annotators = []
    for name in annotator_names:
        try:
            annotators.append(get_annotator(name))
        except Exception:
            pass

    if not annotators:
        print("No valid annotators found")
        return

    for strategy in strategies:
        pipeline = NERPipeline(annotators, dedup_strategy=strategy)
        result = time_pipeline(pipeline, text, iterations)
        result.name = f"{strategy:20} ({len(annotators)} ann)"
        print(result)


def benchmark_text_lengths(iterations: int) -> None:
    """Benchmark with different text lengths.

    Args:
        iterations: Number of iterations.
    """
    print("\nBenchmarking different text lengths...")
    print("-" * 90)

    annotator_names = ["email", "names"]
    annotators = []

    for name in annotator_names:
        try:
            annotators.append(get_annotator(name))
        except Exception:
            pass

    pipeline = NERPipeline(annotators, dedup_strategy="keep_all")

    for length_name, text in SAMPLE_TEXTS.items():
        result = time_pipeline(pipeline, text, iterations)
        result.name = f"{length_name:8} ({len(text):3} chars)"
        print(result)


def print_summary(results: list[BenchmarkResult]) -> None:
    """Print benchmark summary.

    Args:
        results: List of benchmark results.
    """
    if not results:
        return

    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)

    fastest = min(results, key=lambda r: r.avg_time)
    slowest = max(results, key=lambda r: r.avg_time)
    highest_throughput = max(results, key=lambda r: r.entities_per_second)

    print(f"Fastest (avg):        {fastest.name} ({fastest.avg_time*1000:.2f}ms)")
    print(f"Slowest (avg):        {slowest.name} ({slowest.avg_time*1000:.2f}ms)")
    print(f"Highest throughput:   {highest_throughput.name} ({highest_throughput.entities_per_second:.1f} entities/s)")
    print(f"Total iterations:     {sum(r.iterations for r in results)}")


def main() -> None:
    """Run benchmarks."""
    parser = argparse.ArgumentParser(description="Benchmark simple_NER performance")
    parser.add_argument(
        "--annotators",
        type=str,
        default="email,names,locations",
        help="Comma-separated list of annotators to test",
    )
    parser.add_argument(
        "--text",
        type=str,
        default="medium",
        help="Text to use ('short', 'medium', 'long', or custom text)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of iterations per benchmark",
    )
    parser.add_argument(
        "--all-annotators",
        action="store_true",
        help="Test all available annotators",
    )

    args = parser.parse_args()

    # Get text
    if args.text in SAMPLE_TEXTS:
        text = SAMPLE_TEXTS[args.text]
    else:
        text = args.text

    # Get annotators
    if args.all_annotators:
        annotator_names = list_available_annotators()
    else:
        annotator_names = [a.strip() for a in args.annotators.split(",")]

    print("=" * 90)
    print(" SIMPLE_NER BENCHMARK ")
    print("=" * 90)
    print(f"Text length: {len(text)} characters")
    print(f"Iterations: {args.iterations}")
    print(f"Annotators: {', '.join(annotator_names)}")
    print("=" * 90)

    # Run benchmarks
    results = benchmark_single_annotators(annotator_names, text, args.iterations)
    benchmark_dedup_strategies(annotator_names, text, args.iterations)
    benchmark_text_lengths(args.iterations)

    print_summary(results)

    print("\n" + "=" * 90)
    print("BENCHMARK COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()
