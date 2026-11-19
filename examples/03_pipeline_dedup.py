"""
03_pipeline_dedup.py — all four dedup strategies compared
==========================================================
Goal: Show how each dedup strategy resolves overlapping entity spans.
Run:  python examples/03_pipeline_dedup.py
"""

from simple_NER import create_pipeline

# This text is designed to produce overlapping spans:
# "$500" matches both CurrencyAnnotator AND NumberNER,
# "500 items" may also give NumberNER a hit on the bare "500".
TEXT = "I paid $500 dollars for 500 items"

STRATEGIES = ["keep_all", "keep_longest", "keep_higher_confidence", "keep_first"]


def main() -> None:
    print(f"Input: {TEXT!r}\n")
    print(f"{'Strategy':<28} {'entity_type':<18} {'value':<22} {'conf':>5}")
    print("-" * 75)

    for strategy in STRATEGIES:
        pipe = create_pipeline(["currency", "numbers"], dedup_strategy=strategy)
        entities = pipe.process(TEXT)
        if not entities:
            print(f"{strategy:<28} (no entities)")
            continue
        for i, e in enumerate(entities):
            label = strategy if i == 0 else ""
            print(f"{label:<28} {e.entity_type:<18} {e.value!r:<22} {e.confidence:>5.2f}")
        print()

    print("\nWhen to use each strategy:")
    print("  keep_all              — downstream dedup; when you want every candidate")
    print("  keep_longest          — prefer longer/more specific spans")
    print("  keep_higher_confidence— trust the most certain result")
    print("  keep_first            — deterministic when annotator order matters")


if __name__ == "__main__":
    main()
