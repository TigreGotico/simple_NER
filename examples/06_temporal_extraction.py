"""
06_temporal_extraction.py — TemporalNER with anchor_date
=========================================================
Goal: Extract dates, times, and durations; show normalized values.
      anchor_date lets relative expressions ("next Monday") resolve correctly.
Run:  python examples/06_temporal_extraction.py
"""

from datetime import datetime
from simple_NER.annotators.temporal import TemporalNER


def main() -> None:
    # anchor_date anchors relative expressions like "tomorrow" or "next week"
    anchor = datetime(2025, 6, 1, 9, 0, 0)  # Sunday 2025-06-01 09:00
    ann = TemporalNER(lang="en-us", anchor_date=anchor)

    sentences = [
        "The meeting is next Monday at 3pm.",
        "Deliveries usually take two to three business days.",
        "Her birthday is on July 4th.",
        "The contract expires in six months.",
        "We last spoke yesterday around noon.",
        "Schedule it for 2025-09-15 at 14:30.",
        "The event lasts from January 10 to January 15, 2026.",
    ]

    print(f"Anchor date: {anchor}\n")
    print(f"{'Input':<50} {'Type':<12} {'Value'}")
    print("-" * 85)

    for text in sentences:
        entities = list(ann.extract_entities(text))
        if not entities:
            print(f"{text:<50} (none)")
            continue
        for e in entities:
            print(f"{text:<50} {e.entity_type:<12} {e.value!r}")


if __name__ == "__main__":
    main()
