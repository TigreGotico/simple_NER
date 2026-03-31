"""
09_custom_annotator.py — Subclass BaseAnnotator to detect ISBN numbers
======================================================================
Goal: Show the full workflow: write a locale .rx file, implement
      BaseAnnotator, integrate with NERPipeline.
Run:  python examples/09_custom_annotator.py
"""

import os
import re
from typing import Iterator

from simple_NER.annotations import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.pipeline import NERPipeline


# ---------------------------------------------------------------------------
# Step 1: Write the locale regex file.
# In a real package this file lives at simple_NER/locale/en-us/isbn.rx.
# Here we write it next to this script so the example is self-contained.
# ---------------------------------------------------------------------------

LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale_example", "en-us")
LOCALE_FILE = os.path.join(LOCALE_DIR, "isbn.rx")

ISBN_PATTERNS = [
    # ISBN-13 with optional ISBN-13: prefix and hyphens/spaces
    r"ISBN(?:-13)?:?\s*(?:97[89][- ]?(?:\d[- ]?){9}\d)",
    # ISBN-10 with optional ISBN-10: prefix
    r"ISBN(?:-10)?:?\s*(?:\d[- ]?){9}[\dX]",
    # Bare 13-digit EAN starting with 978 or 979
    r"\b97[89]\d{10}\b",
]


def ensure_locale_file() -> None:
    """Write the example locale file if it does not already exist."""
    os.makedirs(LOCALE_DIR, exist_ok=True)
    if not os.path.exists(LOCALE_FILE):
        with open(LOCALE_FILE, "w") as fh:
            for pattern in ISBN_PATTERNS:
                fh.write(pattern + "\n")
        print(f"Wrote locale file: {LOCALE_FILE}")
    else:
        print(f"Locale file already exists: {LOCALE_FILE}")


# ---------------------------------------------------------------------------
# Step 2: Implement the annotator.
# ---------------------------------------------------------------------------


class ISBNAnnotator(BaseAnnotator):
    """Detects ISBN-10 and ISBN-13 codes in text.

    Loads patterns from locale/<lang>/isbn.rx via BaseAnnotator._load_rx.
    """

    name = "isbn"

    def __init__(self, lang: str = "en-us") -> None:
        super().__init__(lang=lang)
        # Load compiled patterns from the locale file.
        # _load_rx looks in simple_NER/locale/<lang>/isbn.rx by default,
        # but here we load directly for the self-contained example.
        self._patterns: list[re.Pattern] = []
        with open(LOCALE_FILE) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    self._patterns.append(re.compile(line, re.IGNORECASE))

    def extract_entities(self, text: str) -> Iterator[Entity]:
        """Yield Entity for each ISBN found in text."""
        for pattern in self._patterns:
            for m in pattern.finditer(text):
                yield Entity(
                    value=m.group(0),
                    entity_type="ISBN",
                    source_text=text,
                    confidence=0.98,
                    spans=[(m.start(), m.end())],
                    data={"start": m.start(), "end": m.end()},
                )


# ---------------------------------------------------------------------------
# Step 3: Use it in a pipeline.
# ---------------------------------------------------------------------------


def main() -> None:
    ensure_locale_file()

    ann = ISBNAnnotator(lang="en-us")
    pipe = NERPipeline(dedup_strategy="keep_longest")
    pipe.add_annotator(ann)

    texts = [
        "See ISBN-13: 978-3-16-148410-0 for the reference implementation.",
        "The textbook (ISBN 0-306-40615-2) is out of print.",
        "Catalogue nos: 9780131101630 and 9780201633610.",
        "No ISBNs mentioned in this sentence.",
    ]

    for text in texts:
        print(f"\nInput: {text}")
        entities = list(pipe.process(text))
        if not entities:
            print("  (none)")
        for e in entities:
            print(f"  [{e.entity_type}] {e.value!r}  conf={e.confidence:.2f}")


if __name__ == "__main__":
    main()
