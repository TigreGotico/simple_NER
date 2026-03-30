# simple_NER

Rule-based Named Entity Recognition with multiple interchangeable backends and an OVOS Intent Transformer plugin.

## Architecture

```
NERWrapper  (simple_NER.annotators)
  └── delegates to registered detectors (any callable)

SimpleNER   (simple_NER)           — keyword/example matching
RuleNER     (simple_NER.rules)     — simplematch pattern matching
RegexNER    (simple_NER.rules.rx)  — regex pattern matching

NERPipeline (simple_NER.pipeline)  — combines multiple annotators, deduplication
AsyncNERPipeline                   — concurrent annotator execution

SimpleNERIntentTransformer (simple_NER.opm) — OVOS opm.transformer.intent plugin
```

All extractors yield `Entity` objects or JSON dicts (`as_json=True`).

## Entity fields

| Field | Type | Description |
|---|---|---|
| `value` | `str` | Extracted surface form |
| `entity_type` | `str` | Label (e.g. `"email"`, `"City"`) |
| `source_text` | `str` | Full input string |
| `confidence` | `float` | Score in `[0, 1]` |
| `spans` | `list[tuple[int,int]]` | `(start, end)` character positions |
| `indexes` | `list[int]` | Start positions |
| `rules` | `list` | Rules that produced this entity |
| `data` | `dict` | Arbitrary annotator metadata |

Nested `data` dicts are accessible via dot-notation (`_SimpleNamespace`). `data["value"]` is remapped to `data_value` to avoid shadowing `Entity.value`.

## Built-in annotators

| Class | Factory key | Dependency |
|---|---|---|
| `SimpleNER` | — | `quebra_frases` |
| `RuleNER` | — | `simplematch` |
| `RegexNER` | — | stdlib |
| `NERWrapper` | — | — |
| `EmailAnnotator` | `"email"` | stdlib |
| `NamesNER` | `"names"` | `quebra_frases` |
| `LocationNER` | `"locations"` | bundled JSON |
| `TemporalNER` | `"temporal"` | `ovos-date-parser` |
| `NumberNER` | `"numbers"` | `ovos-number-parser` |
| `LookUpNER` | `"lookup"` | — |
| `URLAnnotator` | `"url"` | stdlib |
| `PhoneAnnotator` | `"phone"` | stdlib |
| `CurrencyAnnotator` | `"currency"` | `ovos-number-parser` |
| `DateAnnotator` | `"date"` | `ovos-date-parser` |
| `OrganizationAnnotator` | `"organization"` | `quebra_frases` |
| `HashtagAnnotator` | `"hashtag"` | stdlib |

## OVOS plugin

Entry point group: `opm.transformer.intent`
Plugin ID: `simple-ner-transformer`
Base class: `IntentTransformer` — `ovos_plugin_manager.templates.transformers`

Runs after intent matching; injects NER entities into `intent.match_data` without overwriting keys already set by the intent engine. See `simple_NER/opm.py`.

## Installation

```bash
pip install simple_NER                   # core only
pip install "simple_NER[dev]"            # with test/lint tools
```

## Quick start

```python
from simple_NER.annotators.factory import create_pipeline

pipeline = create_pipeline(["email", "names", "locations"])
for e in pipeline.process("John lives in Lisbon, email: john@example.com"):
    print(e.value, "->", e.entity_type)
```

## Key classes

- `Entity` — `simple_NER/__init__.py:16`
- `_SimpleNamespace` — `simple_NER/__init__.py:111`
- `SimpleNER` — `simple_NER/__init__.py:124`
- `Rule` — `simple_NER/rules/__init__.py:7`
- `RuleNER` — `simple_NER/rules/__init__.py:32`
- `RegexNER` — `simple_NER/rules/rx.py:7`
- `NERWrapper` — `simple_NER/annotators/__init__.py:8`
- `NERPipeline` — `simple_NER/pipeline.py`
- `SimpleNERIntentTransformer` — `simple_NER/opm.py:47`

## Further reading

- [API Reference](API.md)
- [Installation](INSTALLATION.md)
- [Tutorials](TUTORIALS.md)
- [FAQ](FAQ.md)
- [Migration](MIGRATION.md)
