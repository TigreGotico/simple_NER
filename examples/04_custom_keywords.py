"""
04_custom_keywords.py — SimpleNER with custom product names
===========================================================
Goal: Define entity types from examples; use is_match, entity_lookup,
      in_place_annotation.
Run:  python examples/04_custom_keywords.py
"""

from simple_NER import SimpleNER


def main() -> None:
    ner = SimpleNER()

    # Register entity types by example
    ner.add_entity_examples(
        "product",
        ["Widget Pro", "Gadget X", "Super Tool 3000", "MegaWidget", "BasicKit"],
    )
    ner.add_entity_examples(
        "department",
        ["engineering", "marketing", "sales", "legal", "finance", "operations"],
    )
    ner.add_entity_examples(
        "priority",
        ["urgent", "high priority", "low priority", "critical", "routine"],
    )

    sentences = [
        "Please send two Widget Pro units to the engineering team.",
        "Marketing ordered a MegaWidget for the trade show — urgent.",
        "The legal department reviewed the BasicKit contract.",
        "No known entities in this sentence.",
    ]

    # --- entity_lookup ---
    print("=== entity_lookup ===")
    for text in sentences:
        print(f"\nInput: {text!r}")
        entities = list(ner.extract_entities(text))
        if not entities:
            print("  (none)")
        for e in entities:
            print(f"  [{e.entity_type}] {e.value!r}")

    # --- is_match ---
    print("\n=== is_match ===")
    test = "The engineering team needs a Super Tool 3000 ASAP — critical."
    for label in ("product", "department", "priority", "location"):
        print(f"  is_match({label!r}): {ner.is_match(test, label)}")

    # --- in_place_annotation ---
    print("\n=== in_place_annotation ===")
    for text in sentences:
        annotated = ner.in_place_annotation(text)
        print(f"  {annotated}")


if __name__ == "__main__":
    main()
