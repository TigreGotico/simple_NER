# simple_NER

Rule-based Named Entity Recognition with multiple interchangeable backends and an OVOS Intent Transformer plugin.

## Architecture

```
create_pipeline(names, dedup_strategy)
        │
        ▼
  NERPipeline / AsyncNERPipeline
        │  add_annotator(annotator)
        ▼
  BaseAnnotator subclasses          ← locale/*.rx, *.intent, *.txt
        │  extract_entities(text)
        ▼
  Entity(value, entity_type, confidence, data, spans, ...)
```

**Core classes:**

- `Entity` — `simple_NER/annotations.py` — result dataclass
- `SimpleNER` — `simple_NER/simple_ner.py` — keyword/example NER
- `NERWrapper` — `simple_NER/pipeline.py` — wraps a callable as an annotator
- `NERPipeline` — `simple_NER/pipeline.py` — aggregates annotators, applies dedup
- `AsyncNERPipeline` — `simple_NER/async_pipeline.py` — async variant of NERPipeline
- `BaseAnnotator` — `simple_NER/annotators/base.py` — base class for all annotators

---

## Entity

`Entity` — `simple_NER/annotations.py`

| Field | Type | Description |
|:---|:---|:---|
| `value` | str | Extracted text span |
| `entity_type` | str | Label (e.g. `"email"`, `"phone"`, `"Location"`) |
| `source_text` | str | Full input text |
| `confidence` | float | 0.0–1.0 |
| `spans` | list[tuple[int,int]] | Character span(s) |
| `indexes` | list[int] | Token indexes |
| `data` | dict | Annotator-specific metadata |
| `rules` | list | Rules that fired |

`Entity.as_json()` — returns a JSON-serializable dict of all fields.

---

## SimpleNER

`SimpleNER` — `simple_NER/simple_ner.py`

Keyword and example-based NER. Uses ahocorasick-ner for efficient multi-pattern matching.

```python
from simple_NER import SimpleNER

ner = SimpleNER()
ner.add_entity_examples("color", ["red", "green", "blue", "yellow"])

for entity in ner.extract_entities("the car is bright red"):
    print(entity.value, entity.entity_type)  # red  color

print(ner.is_match("I like blue", "color"))   # True
print(ner.in_place_annotation("a red car"))   # a {red:color} car
```

**Methods:**

| Method | Description |
|:---|:---|
| `add_entity_examples(name, examples)` | Register a new entity type with example strings |
| `entity_lookup(text)` | Yield `Entity` objects for all known types found in text |
| `extract_entities(text)` | Alias for `entity_lookup` |
| `is_match(text, entity)` | Return True if text contains any example for the entity type |
| `in_place_annotation(text)` | Return text with entities annotated as `{value:type}` |

---

## NERWrapper

`NERWrapper` — `simple_NER/pipeline.py`

Wraps any callable `(text: str) -> Iterable[Entity]` as an annotator for use in a pipeline.

```python
from simple_NER.pipeline import NERWrapper

def my_detector(text):
    if "dog" in text:
        yield Entity("dog", "animal", text, confidence=0.9)

wrapper = NERWrapper(my_detector)
```

**Methods:**

| Method | Description |
|:---|:---|
| `add_detector(parser)` | Register an additional callable detector |
| `extract_entities(text)` | Run all registered detectors, yield merged results |

---

## NERPipeline

`NERPipeline` — `simple_NER/pipeline.py`

Aggregates multiple annotators and applies a dedup strategy to resolve overlapping spans.

```python
from simple_NER.pipeline import NERPipeline
from simple_NER.annotators.email import EmailAnnotator
from simple_NER.annotators.phone import PhoneAnnotator

pipe = NERPipeline(dedup_strategy="keep_longest")
pipe.add_annotator(EmailAnnotator())
pipe.add_annotator(PhoneAnnotator())

for entity in pipe.process("email me at foo@bar.com or call 555-1234"):
    print(entity.entity_type, entity.value)
```

**Dedup strategies:**

| Strategy | Behaviour |
|:---|:---|
| `keep_all` | Return every entity, including overlapping spans |
| `keep_longest` | Prefer longer span when two overlap |
| `keep_higher_confidence` | Prefer higher-confidence entity when two overlap |
| `keep_first` | Prefer the first entity encountered when two overlap |

**Methods:**

| Method | Signature | Description |
|:---|:---|:---|
| `add_annotator` | `(annotator)` | Register an annotator instance |
| `remove_annotator` | `(name: str)` | Unregister by name |
| `process` | `(text: str) -> list[Entity]` | Extract and dedup entities |
| `process_generator` | `(text: str) -> Iterator[Entity]` | Streaming variant |

**Factory function:**

```python
from simple_NER import create_pipeline

pipe = create_pipeline(
    ["email", "phone", "temporal"],
    dedup_strategy="keep_longest",
    lang="en-us"
)
```

---

## AsyncNERPipeline

`AsyncNERPipeline` — `simple_NER/async_pipeline.py`

Async-capable pipeline for concurrent batch processing.

```python
import asyncio
from simple_NER.async_pipeline import AsyncNERPipeline

pipe = AsyncNERPipeline(dedup_strategy="keep_longest")
pipe.add_annotator(...)

async def main():
    # single text
    entities = await pipe.process_async("Call me at 555-1234")
    # batch
    results = await pipe.process_batch_async(sentences, max_concurrency=10)
    for sentence_entities in results:
        for e in sentence_entities:
            print(e.entity_type, e.value)

asyncio.run(main())
```

**Additional methods vs NERPipeline:**

| Method | Signature | Description |
|:---|:---|:---|
| `process_async` | `(text: str) -> Awaitable[list[Entity]]` | Async single-text processing |
| `process_batch_async` | `(texts, max_concurrency=10) -> Awaitable[list[list[Entity]]]` | Process many texts with bounded concurrency |

---

## Annotators

### EmailAnnotator / EmailNER

Factory keys: `email`, `email_regex`

```python
from simple_NER.annotators.email import EmailAnnotator
ann = EmailAnnotator()
```

`data` fields: `local_part`, `domain`, `start`, `end`

---

### NamesNER

Factory key: `names`

Heuristic person-name detection using stopwords and capitalization. Confidence 0.65–0.8.
`entity_type="Noun"`. English / Latin script only.

---

### LocationNER

Factory keys: `locations`, `countries`, `cities`

```python
from simple_NER.annotators.locations import LocationNER
ann = LocationNER(
    include_countries=True,
    include_capitals=True,
    include_cities=False,
    label_confidence={"City": 0.7, "Country": 0.95, "Capital": 0.9}
)
```

`data` fields: `country_code`, `label`, `start`, `end`

---

### TemporalNER

Factory keys: `temporal`, `datetime`, `duration`

```python
from simple_NER.annotators.temporal import TemporalNER
from datetime import datetime
ann = TemporalNER(lang="en-us", anchor_date=datetime(2025, 1, 1))
```

Uses `ovos-date-parser` internally.

---

### NumberNER

Factory keys: `numbers`, `written_numbers`

```python
from simple_NER.annotators.numbers import NumberNER
ann = NumberNER(lang="en-us")
```

`data` fields: `number` (str, digit form), `start`, `end`

---

### LookUpNER

Factory keys: `lookup`, `wordlist`

```python
from simple_NER.annotators.lookup import LookUpNER
ann = LookUpNER(lang="en-us", label_confidence={"Product": 0.9})
ann.add_wordlist("Product", ["Widget Pro", "Gadget X", "Super Tool"])
ann.remove_wordlist("Product")
```

`label_confidence` maps entity label → confidence override.

---

### URLAnnotator

Factory keys: `url`, `urls`

`data` fields: `protocol`, `start`, `end`

---

### PhoneAnnotator

Factory keys: `phone`, `phone_number`

```python
from simple_NER.annotators.phone import PhoneAnnotator
ann = PhoneAnnotator(require_country_code=False, min_length=7)
```

`data` fields: `digits`, `digit_count`, `type` (international/us_national/local/other), `has_country_code`, `start`, `end`

---

### CurrencyAnnotator

Factory keys: `currency`, `money`

`data` fields: `amount` (float), `currency` (ISO 4217 code), `currency_symbol`, `start`, `end`

---

### OrganizationAnnotator

Factory keys: `organization`, `org`, `company`

```python
from simple_NER.annotators.organizations import OrganizationAnnotator
ann = OrganizationAnnotator(strict_mode=False)
```

`data` fields: `org_type` (company/educational/medical/other), `start`, `end`

---

### HashtagAnnotator

Factory keys: `hashtag`, `hashtags`, `tag`

`data` fields: `tag_type` (shouting/lowercase/CamelCase/underscored/alphanumeric/mixed), `start`, `end`

---

### DateAnnotator

Factory keys: `date`, `dates`

```python
from simple_NER.annotators.dates import DateAnnotator
ann = DateAnnotator(lang="en-us")
```

`data` fields: `year`, `month`, `day`, `format`, `start`, `end`

---

## Locale / i18n System

Annotators load language-specific patterns from `simple_NER/locale/<lang>/`.

| Extension | Content | Loader function |
|:---|:---|:---|
| `.rx` | One raw regex per line | `load_rx(name, lang)` — `simple_NER/utils.py` |
| `.intent` | NL templates `{variable}` → named capture group | `load_intents(name, lang)` — `simple_NER/utils.py` |
| `.txt` | Plain wordlist, one entry per line | `load_wordlist(name, lang)` — `simple_NER/utils.py` |

All loaders fall back to `en-us` when no language file is found.

`intent_to_regex("{amount} dollars")` → `re.compile(r"(?P<amount>.+?)\ dollars")` — `simple_NER/utils.py`

**Convenience wrappers inside `BaseAnnotator`** — `simple_NER/annotators/base.py`:
- `self._load_rx(name)` — calls `load_rx(name, self.lang)`
- `self._load_intents(name)` — calls `load_intents(name, self.lang)`

**Existing locale data:**
- `en-us`: phone, email, url, hashtag, currency, organization, date_months
- `de-de`: currency, organization, date_months
- `es`, `fr`, `it`, `nl`, `pt`: date_months

**Adding a new language:**

1. Create `simple_NER/locale/<lang>/` (e.g. `ja-jp/`)
2. Add any `.rx`, `.intent`, or `.txt` files that differ from `en-us`
3. Pass `lang="ja-jp"` when constructing annotators that support it

---

## Extending simple_NER

Subclass `BaseAnnotator` — `simple_NER/annotators/base.py`:

```python
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.annotations import Entity


class MyAnnotator(BaseAnnotator):
    """Detects widget product codes like WGT-12345."""

    name = "widget"

    def __init__(self, lang: str = "en-us") -> None:
        super().__init__(lang=lang)
        # load patterns from locale/en-us/widget.rx
        self._patterns = self._load_rx("widget")

    def extract_entities(self, text: str):
        """Yield Entity objects for each widget code found in text."""
        for pattern in self._patterns:
            for m in pattern.finditer(text):
                yield Entity(
                    value=m.group(0),
                    entity_type="WidgetCode",
                    source_text=text,
                    confidence=0.95,
                    spans=[(m.start(), m.end())],
                    data={"start": m.start(), "end": m.end()},
                )
```

Locale file `simple_NER/locale/en-us/widget.rx`:
```
WGT-\d{5}
WIDGET-[A-Z]{2}\d{3}
```

Register with `create_pipeline` by passing the instance directly to `NERPipeline.add_annotator`,
or use `NERWrapper` to wrap a plain callable.

---

## OVOS Plugin

Class: `SimpleNERIntentTransformer` — `simple_NER/opm.py`
Entry-point group: `opm.transformer.intent`, key: `simple-ner-transformer`, priority 50.

Config keys in `mycroft.conf`:

| Key | Type | Default | Description |
|:---|:---|:---|:---|
| `annotators` | list[str] | `["email","phone","temporal","currency"]` | Factory keys to load |
| `confidence_threshold` | float | `0.6` | Minimum confidence to inject entity |
| `lang` | str | `"en-us"` | Language for all annotators |

The transformer runs the pipeline on every utterance and injects recognized entities into
`match_data` under their `entity_type` keys before intent handling.

---

## Links

- [docs/TUTORIALS.md](TUTORIALS.md)
- [docs/API.md](API.md)
- [docs/FAQ.md](FAQ.md)
- [examples/README.md](../examples/README.md)
- [GitHub](https://github.com/OpenJarbas/simple_NER)
