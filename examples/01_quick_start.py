"""
01_quick_start.py — create_pipeline basics
==========================================
Goal: Extract contact info and temporal entities from a paragraph.
Run:  python examples/01_quick_start.py
"""

from simple_NER import create_pipeline


def main() -> None:
    # Build a pipeline from factory keys.
    # dedup_strategy="keep_longest" resolves overlapping spans by preferring
    # the longer match (e.g. "$50 dollars" beats "$50").
    pipe = create_pipeline(
        ["email", "phone", "url", "currency", "temporal"],
        dedup_strategy="keep_longest",
    )

    text = (
        "Hi team, please contact sales@acme.com or call +1-800-555-0199 for support. "
        "Our summer promo runs until 2025-08-31 — save $49.99 on every order. "
        "Details at https://acme.com/promo."
    )

    print(f"Input: {text}\n")
    print(f"{'Entity type':<18} {'Value':<35} {'Confidence':>10}")
    print("-" * 65)

    for entity in pipe.process(text):
        print(
            f"{entity.entity_type:<18} {entity.value!r:<35} {entity.confidence:>10.2f}"
        )


if __name__ == "__main__":
    main()
