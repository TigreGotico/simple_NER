"""
05_location_extraction.py — LocationNER with label_confidence
=============================================================
Goal: Extract countries, capitals, and cities from news-style text;
      show entity label and per-label confidence.
Run:  python examples/05_location_extraction.py
"""

from simple_NER.annotators.locations import LocationNER


def main() -> None:
    # label_confidence lets you tune confidence per entity sub-type.
    # Cities are noisier (more false positives) so we assign lower confidence.
    ann = LocationNER(
        include_countries=True,
        include_capitals=True,
        include_cities=True,
        label_confidence={
            "Country": 0.95,
            "Capital": 0.90,
            "City": 0.70,
        },
    )

    paragraphs = [
        (
            "World leaders from France, Germany, and Japan met in Paris on Thursday "
            "to discuss climate policy. Representatives from Brazil and Canada also attended."
        ),
        (
            "Flooding has affected parts of Bangladesh and Pakistan. "
            "Aid is being coordinated through Geneva and New York."
        ),
        (
            "The tech conference in Berlin drew attendees from Silicon Valley, London, "
            "and Tokyo. Several startups from Tel Aviv showcased new AI tools."
        ),
    ]

    for para in paragraphs:
        print(f"\nInput: {para[:80]}...")
        print(f"{'Label':<12} {'Value':<20} {'Confidence':>10}  {'Country Code'}")
        print("-" * 55)
        entities = list(ann.extract_entities(para))
        if not entities:
            print("  (no locations found)")
        seen = set()
        for e in entities:
            key = (e.value, e.entity_type)
            if key in seen:
                continue
            seen.add(key)
            country_code = e.data.get("country_code", "")
            print(
                f"  {e.entity_type:<10} {e.value!r:<20} {e.confidence:>10.2f}"
                f"  {country_code}"
            )


if __name__ == "__main__":
    main()
