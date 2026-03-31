# Tutorials

Step-by-step tutorials for common simple_NER use cases.

---

## 1. Basic Extraction with `create_pipeline`

**Goal:** Extract entities from free text using the factory function.

```python
from simple_NER import create_pipeline

pipe = create_pipeline(
    ["email", "phone", "url", "currency", "temporal"],
    dedup_strategy="keep_longest"
)

text = (
    "Contact sales@acme.com or call +1-800-555-0199. "
    "Visit https://acme.com. Our Q3 sale ends 2025-09-30 — save $49.99!"
)

for entity in pipe.process(text):
    print(f"{entity.entity_type:15} {entity.value!r:35} conf={entity.confidence:.2f}")
```

Sample output:
```
email           'sales@acme.com'                    conf=1.00
phone           '+1-800-555-0199'                   conf=0.90
url             'https://acme.com'                  conf=1.00
date            '2025-09-30'                        conf=0.85
currency        '$49.99'                            conf=0.95
```

---

## 2. Custom Keyword NER with `SimpleNER`

**Goal:** Define your own entity types from examples, then use `is_match`, `entity_lookup`, and `in_place_annotation`.

```python
from simple_NER import SimpleNER

ner = SimpleNER()
ner.add_entity_examples("color", ["red", "green", "blue", "yellow", "purple"])
ner.add_entity_examples("size", ["small", "medium", "large", "extra large", "XL"])

text = "I want a large blue shirt"

# Iterate entities
for entity in ner.extract_entities(text):
    print(entity.entity_type, repr(entity.value))
# size   'large'
# color  'blue'

# Boolean check
print(ner.is_match(text, "color"))   # True
print(ner.is_match(text, "size"))    # True
print(ner.is_match(text, "animal"))  # False

# Annotated string
print(ner.in_place_annotation(text))
# I want a {large:size} {blue:color} shirt
```

---

## 3. Pipeline Dedup Strategies

**Goal:** Understand when to use each strategy.

```python
from simple_NER import create_pipeline

text = "I paid $500 dollars for 500 items"

for strategy in ("keep_all", "keep_longest", "keep_higher_confidence", "keep_first"):
    pipe = create_pipeline(["currency", "numbers"], dedup_strategy=strategy)
    entities = pipe.process(text)
    print(f"{strategy:25} → {[(e.entity_type, e.value) for e in entities]}")
```

Sample output:
```
keep_all                  → [('currency', '$500'), ('number', '500'), ('number', '500')]
keep_longest              → [('currency', '$500 dollars'), ('number', '500')]
keep_higher_confidence    → [('currency', '$500'), ('number', '500')]
keep_first                → [('currency', '$500'), ('number', '500')]
```

**When to use each:**

| Strategy | Use case |
|:---|:---|
| `keep_all` | Downstream dedup; analysis pipelines where you want every candidate |
| `keep_longest` | Named entities where longer span = more specific (e.g. `"New York City"` over `"New York"`) |
| `keep_higher_confidence` | Mixed-confidence annotators; trust the most certain result |
| `keep_first` | Deterministic output when annotator order is meaningful |

---

## 4. Multi-Language Pipeline

**Goal:** Use German locale for dates, currency, and numbers.

```python
from simple_NER import create_pipeline

pipe = create_pipeline(
    ["temporal", "currency", "numbers"],
    dedup_strategy="keep_longest",
    lang="de-de"
)

texts = [
    "Der Preis beträgt 49,99 € am 15. März 2025.",
    "Wir haben drei Artikel für 1.200,00 EUR bestellt.",
]

for text in texts:
    print(f"\nText: {text}")
    for entity in pipe.process(text):
        print(f"  {entity.entity_type:12} {entity.value!r}")
```

Sample output:
```
Text: Der Preis beträgt 49,99 € am 15. März 2025.
  currency     '49,99 €'
  date         '15. März 2025'

Text: Wir haben drei Artikel für 1.200,00 EUR bestellt.
  number       'drei'
  currency     '1.200,00 EUR'
```

**Note:** Pass `lang="de-de"` to `create_pipeline` — it is forwarded to all annotators that
support it. Annotators without locale data for `de-de` fall back to `en-us` automatically.

---

## 5. Custom Wordlist with LookUpNER

**Goal:** Extract custom entity types at runtime using `add_wordlist` / `remove_wordlist`.

```python
from simple_NER.annotators.lookup import LookUpNER

ann = LookUpNER(lang="en-us", label_confidence={"Product": 0.9, "InternalCode": 0.85})

# Register wordlists at runtime
ann.add_wordlist("Product", ["Widget Pro", "Gadget X", "Super Tool 3000"])
ann.add_wordlist("InternalCode", ["SKU-001", "SKU-002", "PROJ-ALPHA"])

texts = [
    "Please ship two Widget Pro units with SKU-001 by Friday.",
    "The PROJ-ALPHA team is testing Gadget X.",
]

for text in texts:
    for entity in ann.extract_entities(text):
        print(f"{entity.entity_type:15} {entity.value!r:20} conf={entity.confidence:.2f}")

# Remove a wordlist when no longer needed
ann.remove_wordlist("InternalCode")
```

Sample output:
```
Product         'Widget Pro'         conf=0.90
InternalCode    'SKU-001'            conf=0.85
Product         'Gadget X'           conf=0.90
InternalCode    'PROJ-ALPHA'         conf=0.85
```

---

## 6. Building a Custom Annotator

**Goal:** Subclass `BaseAnnotator` to detect ISBN numbers using a locale `.rx` file.

**Step 1 — Create the locale file** `simple_NER/locale/en-us/isbn.rx`:
```
ISBN(?:-1[03])?:?\s*(?:[0-9]{9}[0-9X]|(?:[0-9]{3}-?){4}[0-9X])
```

**Step 2 — Implement the annotator:**

```python
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.annotations import Entity


class ISBNAnnotator(BaseAnnotator):
    """Detects ISBN-10 and ISBN-13 codes in text."""

    name = "isbn"

    def __init__(self, lang: str = "en-us") -> None:
        super().__init__(lang=lang)
        self._patterns = self._load_rx("isbn")  # loads locale/en-us/isbn.rx

    def extract_entities(self, text: str):
        """Yield Entity objects for each ISBN found in text."""
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
```

**Step 3 — Use it:**

```python
from simple_NER.pipeline import NERPipeline

pipe = NERPipeline(dedup_strategy="keep_longest")
pipe.add_annotator(ISBNAnnotator())

for entity in pipe.process("See ISBN-13: 978-3-16-148410-0 for details"):
    print(entity.entity_type, entity.value)
# ISBN  ISBN-13: 978-3-16-148410-0
```

---

## 7. Async Batch Processing

**Goal:** Process many sentences concurrently with `AsyncNERPipeline`.

```python
import asyncio
from simple_NER.async_pipeline import AsyncNERPipeline
from simple_NER.annotators.email import EmailAnnotator
from simple_NER.annotators.phone import PhoneAnnotator
from simple_NER.annotators.url import URLAnnotator

sentences = [
    "Reach Alice at alice@example.com",
    "Call Bob: +44 20 7946 0958",
    "Visit https://example.org for more info",
    "Email support@corp.io or call 1-800-FLOWERS",
    "No contact info here",
    "Both info@test.com and https://test.com/page",
    "International: +49-89-12345678",
    "US local: (212) 555-3456",
    "Check https://secure.bank.example for rates",
    "Fax: +1 (888) 555-0101",
]

pipe = AsyncNERPipeline(dedup_strategy="keep_longest")
pipe.add_annotator(EmailAnnotator())
pipe.add_annotator(PhoneAnnotator())
pipe.add_annotator(URLAnnotator())


async def main() -> None:
    results = await pipe.process_batch_async(sentences, max_concurrency=5)
    for text, entities in zip(sentences, results):
        found = [(e.entity_type, e.value) for e in entities]
        print(f"{text[:45]!r:50} → {found}")


asyncio.run(main())
```

---

## 8. OVOS Plugin Configuration

**Goal:** Configure `SimpleNERIntentTransformer` in `mycroft.conf`.

Add the following to your `~/.config/mycroft/mycroft.conf` (or the system-wide equivalent):

```json
{
  "intent_transformers": {
    "simple-ner-transformer": {
      "annotators": ["email", "phone", "temporal", "currency", "location"],
      "confidence_threshold": 0.65,
      "lang": "en-us"
    }
  }
}
```

When OVOS processes an utterance such as *"Send $50 to alice@example.com"*, the transformer
runs the pipeline and injects recognized entities into `match_data` before intent handling:

```python
# What match_data looks like after transformation:
{
    "utterance": "Send $50 to alice@example.com",
    "entities": [
        {"entity_type": "currency", "value": "$50",              "confidence": 0.95, "data": {"amount": 50.0, "currency": "USD"}},
        {"entity_type": "email",    "value": "alice@example.com","confidence": 1.0,  "data": {"local_part": "alice", "domain": "example.com"}},
    ]
}
```

Only entities with `confidence >= confidence_threshold` are injected.
The plugin is auto-discovered via the `opm.transformer.intent` entry-point group —
no import is needed; installing `simple_NER` is sufficient.
