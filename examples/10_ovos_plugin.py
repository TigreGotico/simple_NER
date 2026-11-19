"""
10_ovos_plugin.py — SimpleNERIntentTransformer data flow (no OVOS runtime)
===========================================================================
Goal: Show the plugin config and what match_data looks like after the
      transformer injects recognized entities.  No actual OVOS runtime needed.
Run:  python examples/10_ovos_plugin.py
"""

import json
from simple_NER import create_pipeline


# ---------------------------------------------------------------------------
# mycroft.conf snippet that activates the plugin
# ---------------------------------------------------------------------------

MYCROFT_CONF_SNIPPET = {
    "intent_transformers": {
        "simple-ner-transformer": {
            "annotators": ["email", "phone", "temporal", "currency", "location"],
            "confidence_threshold": 0.65,
            "lang": "en-us",
        }
    }
}

print("=== mycroft.conf snippet ===")
print(json.dumps(MYCROFT_CONF_SNIPPET, indent=2))


# ---------------------------------------------------------------------------
# Simulate what SimpleNERIntentTransformer does to match_data.
# The real transformer (simple_NER/opm.py) does this inside transform().
# ---------------------------------------------------------------------------

def simulate_transformer(utterance: str, config: dict) -> dict:
    """Return a match_data dict as the transformer would produce it."""
    cfg = config["intent_transformers"]["simple-ner-transformer"]
    pipe = create_pipeline(
        cfg["annotators"],
        dedup_strategy="keep_longest",
        lang=cfg["lang"],
    )
    threshold = cfg["confidence_threshold"]

    entities = [
        {
            "entity_type": e.entity_type,
            "value": e.value,
            "confidence": e.confidence,
            "data": e.data,
        }
        for e in pipe.process(utterance)
        if e.confidence >= threshold
    ]

    return {
        "utterance": utterance,
        "lang": cfg["lang"],
        "entities": entities,
    }


# ---------------------------------------------------------------------------
# Demo utterances
# ---------------------------------------------------------------------------

UTTERANCES = [
    "Send $50 to alice@example.com by next Friday",
    "Book a flight to Paris for 2025-09-20",
    "Call +1-800-555-0100 about the €299 renewal",
]

print("\n=== Simulated match_data after transformer ===")
for utt in UTTERANCES:
    result = simulate_transformer(utt, MYCROFT_CONF_SNIPPET)
    print(f"\nUtterance: {utt!r}")
    if result["entities"]:
        for ent in result["entities"]:
            print(
                f"  [{ent['entity_type']}] {ent['value']!r}  "
                f"conf={ent['confidence']:.2f}  "
                f"data={ent['data']}"
            )
    else:
        print("  (no entities above threshold)")

print(
    "\nNote: in production, SimpleNERIntentTransformer is auto-discovered via the\n"
    "      opm.transformer.intent entry-point group — no import needed."
)
