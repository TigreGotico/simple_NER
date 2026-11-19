#!/usr/bin/env python3
"""Command-line interface for simple_NER.

Usage:
    python -m simple_NER.cli "John lives in Lisbon" --annotators names,locations
    python -m simple_NER.cli --file input.txt --output results.json
    python -m simple_NER.cli --list-annotators
    echo "Contact john@example.com" | python -m simple_NER.cli

Options:
    -h, --help              Show this help message
    -a, --annotators        Comma-separated list of annotators (default: email,names,locations)
    -f, --file              Input file path (default: stdin)
    -o, --output            Output file path (default: stdout)
    --format                Output format: text, json, csv (default: text)
    --dedup                 Deduplication strategy: keep_all, keep_longest,
                            keep_higher_confidence, keep_first (default: keep_all)
    --list-annotators       List all available annotators
    --version               Show version information

Examples:
    # Extract entities from text
    python -m simple_NER.cli "John Doe works at MIT in Cambridge"

    # Use specific annotators
    python -m simple_NER.cli "Email: test@example.com" -a email

    # Process a file and output JSON
    python -m simple_NER.cli --file input.txt --output results.json --format json

    # List available annotators
    python -m simple_NER.cli --list-annotators

    # Read from stdin
    echo "Contact alice@company.org for info" | python -m simple_NER.cli
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from simple_NER import Entity
from simple_NER.annotators.factory import (
    create_pipeline,
    list_available_annotators,
)
from simple_NER.pipeline import NERPipeline


def format_entity_text(entity: Entity, show_spans: bool = False) -> str:
    """Format entity as human-readable text.

    Args:
        entity: Entity to format.
        show_spans: Whether to show character spans.

    Returns:
        Formatted string.
    """
    spans_str = ""
    if show_spans and entity.spans:
        spans_str = f" [{entity.spans[0][0]}-{entity.spans[0][1]}]"

    return f"{entity.value!r:25} -> {entity.entity_type:20} (conf: {entity.confidence:.2f}){spans_str}"


def format_entity_json(entity: Entity) -> dict[str, Any]:
    """Format entity as JSON-serializable dict.

    Args:
        entity: Entity to format.

    Returns:
        Dictionary representation.
    """
    return entity.as_json()


def format_entity_csv(entity: Entity) -> str:
    """Format entity as CSV line.

    Args:
        entity: Entity to format.

    Returns:
        CSV-formatted string.
    """
    spans = entity.spans[0] if entity.spans else (0, 0)
    # Escape quotes in value
    value = entity.value.replace('"', '""')
    return f'"{value}","{entity.entity_type}",{entity.confidence:.2f},{spans[0]},{spans[1]}'


def list_annotators() -> None:
    """Print all available annotators."""
    annotators = list_available_annotators()
    print(f"Available annotators ({len(annotators)}):")
    print("-" * 40)

    for i, name in enumerate(annotators, 1):
        print(f"  {i:2}. {name}")


def process_text(
    text: str,
    annotator_names: list[str],
    dedup_strategy: str,
    output_format: str,
    show_spans: bool = False,
) -> None:
    """Process text and output results.

    Args:
        text: Input text to process.
        annotator_names: List of annotator names to use.
        dedup_strategy: Deduplication strategy.
        output_format: Output format (text, json, csv).
        show_spans: Whether to show character spans.
    """
    try:
        pipeline = create_pipeline(
            annotator_names,
            dedup_strategy=dedup_strategy,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    entities = pipeline.process(text)

    if not entities:
        if output_format == "json":
            print(json.dumps({"text": text, "entities": []}))
        elif output_format == "csv":
            print("value,entity_type,confidence,start,end")
        else:
            print(f"No entities found in: {text!r}")
        return

    if output_format == "json":
        output = {
            "text": text,
            "entities": [format_entity_json(e) for e in entities],
            "count": len(entities),
        }
        print(json.dumps(output, indent=2))

    elif output_format == "csv":
        print("value,entity_type,confidence,start,end")
        for ent in entities:
            print(format_entity_csv(ent))

    else:  # text format
        print(f"Text: {text!r}")
        print(f"Found {len(entities)} entity/entities:")
        print("-" * 60)
        for ent in entities:
            print(format_entity_text(ent, show_spans))


def process_file(
    input_path: str,
    output_path: str | None,
    annotator_names: list[str],
    dedup_strategy: str,
    output_format: str,
) -> None:
    """Process file line by line.

    Args:
        input_path: Path to input file.
        output_path: Path to output file (None for stdout).
        annotator_names: List of annotator names to use.
        dedup_strategy: Deduplication strategy.
        output_format: Output format.
    """
    try:
        with open(input_path, encoding="utf-8") as f:
            lines = f.readlines()
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    results = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            pipeline = create_pipeline(
                annotator_names,
                dedup_strategy=dedup_strategy,
            )
            entities = pipeline.process(line)
            results.append(
                {
                    "text": line,
                    "entities": [format_entity_json(e) for e in entities],
                    "count": len(entities),
                }
            )
        except Exception as e:
            results.append(
                {
                    "text": line,
                    "entities": [],
                    "count": 0,
                    "error": str(e),
                }
            )

    # Output results
    if output_format == "json":
        output = json.dumps(results, indent=2)
    else:
        # Text format for file processing
        output_lines = []
        for result in results:
            output_lines.append(f"Text: {result['text']!r}")
            output_lines.append(f"Found {result['count']} entity/entities:")
            for ent_data in result["entities"]:
                value = ent_data.get("value", "N/A")
                entity_type = ent_data.get("entity_type", "N/A")
                conf = ent_data.get("confidence", 0)
                output_lines.append(f"  {value!r} -> {entity_type} (conf: {conf:.2f})")
            output_lines.append("")
        output = "\n".join(output_lines)

    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Results written to: {output_path}")
        except IOError as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="simple_NER: Extract named entities from text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "text",
        nargs="?",
        default=None,
        help="Text to process (default: read from stdin)",
    )
    parser.add_argument(
        "-a",
        "--annotators",
        type=str,
        default="email,names",
        help="Comma-separated list of annotators (default: email,names)",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Input file path (default: stdin)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--dedup",
        type=str,
        choices=["keep_all", "keep_longest", "keep_higher_confidence", "keep_first"],
        default="keep_all",
        help="Deduplication strategy (default: keep_all)",
    )
    parser.add_argument(
        "--spans",
        action="store_true",
        help="Show character spans in output",
    )
    parser.add_argument(
        "--list-annotators",
        action="store_true",
        help="List all available annotators",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="simple_NER 0.9.0",
    )

    args = parser.parse_args()

    # Handle --list-annotators
    if args.list_annotators:
        list_annotators()
        return

    # Get input text
    if args.file:
        process_file(
            args.file,
            args.output,
            args.annotators.split(","),
            args.dedup,
            args.format,
        )
    else:
        # Get text from argument or stdin
        if args.text:
            text = args.text
        elif not sys.stdin.isatty():
            text = sys.stdin.read().strip()
        else:
            parser.print_help()
            return

        process_text(
            text,
            args.annotators.split(","),
            args.dedup,
            args.format,
            args.spans,
        )


if __name__ == "__main__":
    main()
