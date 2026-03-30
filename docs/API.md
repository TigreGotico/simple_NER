# simple_NER API Reference

## Core Classes

### Entity

The fundamental data structure for representing extracted entities.

```python
from simple_NER import Entity

entity = Entity(
    value="john@example.com",
    entity_type="email",
    source_text="Contact john@example.com",
    confidence=1.0,
    data={"domain": "example.com"}
)
```

**Attributes:**
- `value` (str): The extracted text
- `entity_type` (str): Category label (e.g., "email", "person")
- `source_text` (str): Original input text
- `confidence` (float): Confidence score [0.0-1.0]
- `data` (dict): Additional metadata
- `spans` (list[tuple[int, int]]): Character positions in source_text
- `indexes` (list[int]): Start positions of matches
- `occurrence_number` (int): Number of occurrences

**Methods:**
- `as_json() -> dict`: Serialize to JSON-safe dictionary

---

### SimpleNER

Base class for keyword-based entity recognition.

```python
from simple_NER import SimpleNER

ner = SimpleNER()
ner.add_entity_examples("fruit", ["apple", "banana", "orange"])

for entity in ner.extract_entities("I ate an apple"):
    print(entity.value, entity.entity_type)
```

**Methods:**
- `add_entity_examples(name: str, examples: str | list[str])`: Register examples
- `extract_entities(text: str, as_json: bool = False) -> Generator[Entity, None, None]`: Extract entities
- `entity_lookup(text: str, as_json: bool = False) -> Generator[Entity, None, None]`: Lookup by examples
- `is_match(text: str, entity: str | Entity) -> bool`: Check if entity exists in text
- `in_place_annotation(text: str) -> str`: Annotate text with entity labels

---

## Rule-Based NER

### RuleNER

Pattern-based extraction using simplematch syntax.

```python
from simple_NER.rules import RuleNER

ner = RuleNER()
ner.add_rule("name", "my name is {person}")

for entity in ner.extract_entities("my name is Alice"):
    print(entity.value)  # "Alice"
    print(entity.entity_type)  # "person"
```

**Methods:**
- `add_rule(name: str, rules: str | list[str])`: Add simplematch pattern
- `extract_entities(text: str, as_json: bool = False)`: Extract entities

---

### RegexNER

Regex-based extraction extending RuleNER.

```python
from simple_NER.rules.rx import RegexNER

ner = RegexNER()
ner.add_rule("date", r"\d{2}/\d{2}/\d{4}")

for entity in ner.extract_entities("Date: 12/25/2023"):
    print(entity.value)  # "12/25/2023"
```

**Methods:**
- `add_rule(name: str, rules: str | list[str])`: Add regex pattern
- `add_entity_examples(name: str, examples: str | list[str])`: Add word-boundary examples

---

### NeuralNER

Neural network-based extraction using padatious.

```python
from simple_NER.rules.neural import NeuralNER

ner = NeuralNER()
ner.add_rule("name", "my name is {person}")
ner.add_rule("name", "i am {person}")

for entity in ner.extract_entities("the name is Bob"):
    print(entity.value, entity.confidence)
```

**Note:** Requires `padatious` and `fann2` packages.

---

## Annotator Base Classes

### Annotator (ABC)

Abstract base class for all annotators.

```python
from simple_NER.annotators.base import Annotator

class MyAnnotator(Annotator):
    @property
    def name(self) -> str:
        return "my_annotator"
    
    def extract_entities(self, text: str) -> Generator[Entity, None, None]:
        # Implementation
        pass
```

**Abstract Methods:**
- `name -> str`: Unique identifier
- `extract_entities(text: str) -> Generator[Entity, None, None]`: Extract entities

---

### BaseAnnotator

Concrete base class with common functionality.

```python
from simple_NER.annotators.base import BaseAnnotator
from simple_NER import Entity

class EmailAnnotator(BaseAnnotator):
    @property
    def name(self) -> str:
        return "email"
    
    def annotate(self, text: str) -> Generator[Entity, None, None]:
        # Your extraction logic
        yield Entity(email, "email", source_text=text)
```

**Methods to Implement:**
- `annotate(text: str) -> Generator[Entity, None, None]`: Your extraction logic

**Inherited Methods:**
- `extract_entities(text: str)`: Calls `annotate()`
- `name -> str`: Returns lowercase class name

---

## Built-in Annotators

### EmailNER / EmailAnnotator

Extract email addresses using regex.

```python
from simple_NER.annotators.email_ner import EmailNER

ner = EmailNER()
for ent in ner.extract_entities("Contact test@example.com"):
    print(ent.value)  # "test@example.com"
```

---

### NamesNER

Extract proper nouns (names) using regex.

```python
from simple_NER.annotators.names_ner import NamesNER

ner = NamesNER(confidence_threshold=0.8)
for ent in ner.extract_entities("John Doe met Alice"):
    print(ent.value, ent.confidence)
```

**Parameters:**
- `confidence_threshold` (float): Minimum confidence [0.65-0.8]
- `min_word_length` (int): Minimum word length

---

### LocationNER

Extract countries, capitals, and cities from JSON wordlists.

```python
from simple_NER.annotators.locations_ner import LocationNER

ner = LocationNER(
    include_countries=True,
    include_capitals=True,
    include_cities=True,
    lowercase=False
)
for ent in ner.extract_entities("Lisbon is capital of Portugal"):
    print(ent.value, ent.entity_type)
```

**Parameters:**
- `include_countries` (bool): Extract country names
- `include_capitals` (bool): Extract capital cities
- `include_cities` (bool): Extract all cities
- `lowercase` (bool): Case-insensitive matching

---

### TemporalNER

Extract datetime and duration expressions.

```python
from simple_NER.annotators.temporal_ner import TemporalNER

ner = TemporalNER()

# Datetime
for ent in ner.extract_entities("meeting tomorrow at 3pm"):
    if ent.entity_type == "relative_date":
        print(ent.data)  # {timestamp, isoformat, year, month, day, ...}

# Duration
for ent in ner.extract_entities("wait 5 minutes"):
    if ent.entity_type == "duration":
        print(ent.data)  # {days, seconds, total_seconds, ...}
```

**Parameters:**
- `anchor_date` (datetime): Reference date for relative expressions
- `extract_datetime` (bool): Enable datetime extraction
- `extract_duration` (bool): Enable duration extraction

**Note:** Requires `ovos-date-parser` or `lingua_nostra`.

---

### NumberNER

Extract written numbers.

```python
from simple_NER.annotators.numbers_ner import NumberNER

ner = NumberNER(ordinals=True, short_scale=True)
for ent in ner.extract_entities("three hundred apples"):
    print(ent.value, ent.data["number"])  # "three hundred", "300.0"
```

**Parameters:**
- `ordinals` (bool): Extract ordinal numbers (1st, 2nd, third)
- `short_scale` (bool): US (short) vs UK (long) scale
- `case_sensitive` (bool): Case-sensitive matching

**Note:** Requires `ovos-number-parser` or `lingua_nostra`.

---

### KeywordNER

Extract keywords using RAKE algorithm.

```python
from simple_NER.annotators.keyword_ner import KeywordNER

ner = KeywordNER(lang="en", min_word_length=3)
for ent in ner.extract_entities("Machine learning is amazing"):
    print(ent.value, ent.data["score"])
```

**Parameters:**
- `lang` (str): Language code
- `min_word_length` (int): Minimum keyword length
- `confidence` (float): Minimum confidence threshold

**Note:** Requires `RAKEkeywords`.

---

### UnitsNER

Extract physical quantities and measurements.

```python
from simple_NER.annotators.units_ner import UnitsNER

ner = UnitsNER(lang="en")
for ent in ner.extract_entities("The LHC operates at 13.0 TeV"):
    print(ent.value, ent.entity_type)  # "13.0 TeV", "Energy:Electronvolt"
```

**Parameters:**
- `lang` (str): Language code
- `confidence` (float): Default confidence

**Note:** Requires `quantulum3`.

---

### LookUpNER

Extract entities from wordlist files.

```python
from simple_NER.annotators.lookup_ner import LookUpNER

ner = LookUpNER(lang="en-us")
for ent in ner.extract_entities("The sky is blue"):
    print(ent.value, ent.entity_type)  # "blue", "color"
```

**Parameters:**
- `lang` (str): Language code for resource files
- `case_sensitive` (bool): Case-sensitive matching

**Methods:**
- `add_wordlist(label: str, words: list[str])`: Add custom wordlist
- `remove_wordlist(label: str) -> bool`: Remove wordlist
- `loaded_types -> list[str]`: List loaded entity types

---

## Pipeline

### NERPipeline

Execute multiple annotators with deduplication.

```python
from simple_NER.pipeline import NERPipeline
from simple_NER.annotators.email_ner import EmailNER
from simple_NER.annotators.names_ner import NamesNER

pipeline = NERPipeline(
    annotators=[EmailNER(), NamesNER()],
    dedup_strategy="keep_higher_confidence"
)

entities = pipeline.process("John contacted john@example.com")
for ent in entities:
    print(ent.value, ent.entity_type)
```

**Deduplication Strategies:**
- `"keep_all"`: No deduplication
- `"keep_longest"`: Keep longest entity on overlap
- `"keep_higher_confidence"`: Keep higher confidence entity
- `"keep_first"`: Keep first detected entity

**Methods:**
- `add_annotator(annotator: Annotator)`: Add annotator
- `remove_annotator(name: str) -> bool`: Remove by name
- `process(text: str) -> list[Entity]`: Process and deduplicate
- `process_generator(text: str) -> Generator[Entity, None, None]`: Stream results

---

## Factory

### Factory Functions

Create annotators and pipelines by name.

```python
from simple_NER.annotators.factory import (
    get_annotator,
    create_pipeline,
    list_available_annotators,
    register_annotator
)

# List available
print(list_available_annotators())
# ['email', 'names', 'locations', ...]

# Create single annotator
email_ner = get_annotator("email")

# Create pipeline
pipeline = create_pipeline(
    ["email", "names", "locations"],
    dedup_strategy="keep_higher_confidence"
)

# Register custom annotator
register_annotator("my_annotator", MyCustomAnnotator)
```

**Functions:**
- `get_annotator(name: str, **kwargs) -> Annotator`: Create by name
- `create_pipeline(names: list[str], dedup_strategy: str, **kwargs) -> NERPipeline`: Create pipeline
- `list_available_annotators() -> list[str]`: List registered names
- `register_annotator(name: str, annotator_class: type[Annotator])`: Register custom

---

## Registered Annotators

| Name | Class | Description |
|------|-------|-------------|
| `email` | EmailAnnotator | Email addresses |
| `email_regex` | EmailNER | Email (regex version) |
| `names` | NamesNER | Proper nouns |
| `locations` | LocationNER | Countries, capitals, cities |
| `countries` | LocationNER | Countries only |
| `cities` | LocationNER | Cities only |
| `temporal` | TemporalNER | Datetime and duration |
| `datetime` | TemporalNER | Datetime only |
| `duration` | TemporalNER | Duration only |
| `numbers` | NumberNER | Written numbers |
| `written_numbers` | NumberNER | Written numbers (alias) |
| `keywords` | KeywordNER | RAKE keywords |
| `units` | UnitsNER | Measurements |
| `measurements` | UnitsNER | Measurements (alias) |
| `lookup` | LookUpNER | Wordlist lookup |
| `wordlist` | LookUpNER | Wordlist (alias) |

---

## Migration Guide

### From Old API to New API

**Old:**
```python
from simple_NER.annotators.datetime_ner import DateTimeNER
ner = DateTimeNER()
```

**New:**
```python
from simple_NER.annotators.temporal_ner import TemporalNER
ner = TemporalNER()  # DateTimeNER still works (alias)
```

**Old:**
```python
from simple_NER.annotators import NERWrapper
wrapper = NERWrapper()
wrapper.add_detector(custom_function)
```

**New (still supported):**
```python
# NERWrapper still works
```

**New (recommended):**
```python
from simple_NER.annotators.base import BaseAnnotator

class CustomAnnotator(BaseAnnotator):
    def annotate(self, text):
        # Your logic
        yield Entity(...)
```

---

## Error Handling

All annotators handle errors gracefully:

```python
from simple_NER.annotators.factory import get_annotator

try:
    ner = get_annotator("email")
    entities = list(ner.extract_entities(text))
except Exception as e:
    print(f"Extraction error: {e}")
```

Missing optional dependencies are handled with warnings:

```
WARNING - quantulum3 not installed. UnitsNER will not function.
Install with: pip install quantulum3
```
