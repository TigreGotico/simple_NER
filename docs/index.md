# simple_NER

Rule-based Named Entity Recognition with multiple interchangeable backends.

## Architecture

```
NERWrapper  (simple_NER.annotators)
  └── delegates to registered detectors (any callable)

SimpleNER   (simple_NER)           — keyword/example matching
RuleNER     (simple_NER.rules)     — simplematch pattern matching
RegexNER    (simple_NER.rules.rx)  — regex pattern matching
```

All extractors yield `Entity` objects or JSON dicts (``as_json=True``).

## Entity fields

| Field | Type | Description |
|---|---|---|
| `value` | `str` | Extracted surface form |
| `entity_type` | `str` | Label (e.g. `"person"`) |
| `source_text` | `str` | Full input string |
| `confidence` | `float` | Score in `[0, 1]` |
| `spans` | `list[tuple[int,int]]` | `(start, end)` character positions |
| `indexes` | `list[int]` | Start positions |
| `rules` | `list` | Rules that produced this entity |
| `data` | `dict` | Arbitrary annotator metadata |

Nested `data` dicts are accessible as dot-notation sub-attributes (`_SimpleNamespace`). The `data["value"]` key is remapped to `data_value` to avoid shadowing `Entity.value`.

## Annotator table

| Class | Module | Extra | Dependency |
|---|---|---|---|
| `SimpleNER` | `simple_NER` | core | `quebra_frases` |
| `RuleNER` | `simple_NER.rules` | core | `simplematch` |
| `RegexNER` | `simple_NER.rules.rx` | core | stdlib |
| `NERWrapper` | `simple_NER.annotators` | core | — |
| `DateTimeNER` | `simple_NER.annotators.datetime_ner` | `[datetime]` | `lingua_nostra` |
| `UnitsNER` | `simple_NER.annotators.units_ner` | `[units]` | `quantulum3` |
| `KeywordNER` | `simple_NER.annotators.keyword_ner` | `[keywords]` | `RAKEkeywords` |
| `NltkNER` | `simple_NER.annotators.nltk_ner` | `[nltk]` | `nltk` |
| `SpotlightNER` | `simple_NER.annotators.remote` | `[remote]` | `requests` |

## Installation

```bash
pip install simple_NER                        # core only
pip install "simple_NER[datetime,units]"      # with extras
```

## Quick start

```python
from simple_NER.rules import RuleNER
from simple_NER.rules.rx import RegexNER
from simple_NER.annotators import NERWrapper

# Pattern-based
ner = RuleNER()
ner.add_rule("name", "my name is {person}")
for e in ner.extract_entities("my name is jarbas"):
    print(e.entity_type, e.value)  # person jarbas

# Regex-based
rx = RegexNER()
rx.add_rule("email", r"[\w.+-]+@[\w-]+\.[a-z]{2,}")
for e in rx.extract_entities("contact foo@bar.com"):
    print(e.value)  # foo@bar.com

# Aggregating multiple detectors
wrapper = NERWrapper()
wrapper.add_detector(ner.extract_entities)
wrapper.add_detector(rx.extract_entities)
for e in wrapper.extract_entities("my name is bob, contact bob@example.com"):
    print(e)
```

## Key classes

- `Entity` — `simple_NER/__init__.py:16`
- `_SimpleNamespace` — `simple_NER/__init__.py:111` (replaces `types.new_class()`)
- `SimpleNER` — `simple_NER/__init__.py:124`
- `Rule` — `simple_NER/rules/__init__.py:7`
- `RuleNER` — `simple_NER/rules/__init__.py:32`
- `RegexNER` — `simple_NER/rules/rx.py:7`
- `NERWrapper` — `simple_NER/annotators/__init__.py:8`
