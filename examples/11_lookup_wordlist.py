"""
11_lookup_wordlist.py — LookUpNER with runtime add_wordlist / remove_wordlist
=============================================================================
Goal: Extract custom entity types (product names, internal codes) using
      wordlists registered at runtime.
Run:  python examples/11_lookup_wordlist.py
"""

from simple_NER.annotators.lookup import LookUpNER


def main() -> None:
    # label_confidence maps entity label → confidence override.
    ann = LookUpNER(
        lang="en-us",
        label_confidence={
            "Product": 0.90,
            "InternalCode": 0.85,
            "Department": 0.80,
        },
    )

    # --- Register wordlists ---
    ann.add_wordlist("Product", [
        "Widget Pro",
        "Gadget X",
        "Super Tool 3000",
        "MegaWidget",
        "BasicKit",
    ])
    ann.add_wordlist("InternalCode", [
        "SKU-001", "SKU-002", "SKU-099",
        "PROJ-ALPHA", "PROJ-BETA",
    ])
    ann.add_wordlist("Department", [
        "engineering", "marketing", "sales", "legal", "operations",
    ])

    sentences = [
        "Please ship two Widget Pro units with SKU-001 to the engineering team.",
        "PROJ-ALPHA will use MegaWidget and Gadget X in the prototype.",
        "The legal department reviewed SKU-099 pricing for BasicKit.",
        "No known entities here.",
        "Super Tool 3000 is now assigned to PROJ-BETA in operations.",
    ]

    print("=== With all wordlists ===\n")
    for text in sentences:
        entities = list(ann.extract_entities(text))
        print(f"Input: {text}")
        if not entities:
            print("  (none)")
        for e in entities:
            print(f"  [{e.entity_type}] {e.value!r}  conf={e.confidence:.2f}")
        print()

    # --- Remove a wordlist dynamically ---
    print("=== After remove_wordlist('InternalCode') ===\n")
    ann.remove_wordlist("InternalCode")

    test = "PROJ-ALPHA needs SKU-001 for Widget Pro assembly."
    entities = list(ann.extract_entities(test))
    print(f"Input: {test}")
    for e in entities:
        print(f"  [{e.entity_type}] {e.value!r}  conf={e.confidence:.2f}")
    if not entities:
        print("  (none)")

    print("\n(InternalCode wordlist removed — SKU-001 and PROJ-ALPHA no longer detected)")


if __name__ == "__main__":
    main()
