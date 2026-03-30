# FAQ & Troubleshooting

## General Questions

### Q: What is simple_NER?

**A:** A lightweight rule-based NER library. Extracts named entities via simplematch patterns, regex, and pre-built annotators for common entity types (email, names, locations, dates, numbers, etc.).

### Q: What entity types does it support?

**A:** 16 built-in annotators: email, names, locations (countries/capitals/cities), temporal (datetime/duration), numbers, lookup, URL, phone, currency, organization, hashtag, date. Custom types via `RuleNER` or `RegexNER`.

### Q: What Python versions are supported?

**A:** Python 3.10–3.13.

### Q: How does it compare to spaCy or NLTK?

**A:** simple_NER is lighter and rule-based — no ML models, no training data, easy to customize. spaCy/NLTK are better when statistical accuracy matters more than speed and interpretability.

### Q: What languages are supported?

**A:** Language support varies by annotator:

| Annotator | Language coverage |
|-----------|-------------------|
| `TemporalNER`, `NumberNER` | Multi-language via `ovos-date-parser` / `ovos-number-parser`; pass `lang="de-de"` etc. |
| `DateAnnotator` | Written month names in EN/ES/FR/DE/PT/IT/NL; numeric formats are language-agnostic |
| `CurrencyAnnotator` | Currency words in EN/ES/FR/DE/PT/IT/NL; symbols/ISO codes are language-agnostic |
| `OrganizationAnnotator` | Company suffixes for DE/FR/ES/PT/IT/NL/BE + English; accented Latin characters in name regex |
| `HashtagAnnotator` | Fully Unicode-aware (`re.UNICODE`) — matches hashtags in any script |
| `LocationNER` | Language-agnostic (bundled JSON city/country names) |
| `EmailAnnotator`, `URLAnnotator`, `PhoneAnnotator` | Language-agnostic (structural patterns) |
| `LookUpNER` | Per-language via `.entity` resource files under `res/<lang>/` |

Pass `lang` to any annotator or to `create_pipeline(names, lang="de-de")` — the factory forwards it to all constructors.

### Q: Is there an OVOS plugin?

**A:** Yes. `SimpleNERIntentTransformer` (`simple_NER.opm`) is an `opm.transformer.intent` plugin. It runs after intent matching and injects extracted entities into `intent.match_data`. Plugin ID: `simple-ner-transformer`.

```json
{
    "intent_transformers": {
        "simple-ner-transformer": {
            "annotators": ["email", "names", "locations", "temporal", "numbers"],
            "confidence_threshold": 0.5
        }
    }
}
```

---

## Installation Issues

### "No module named 'simple_NER'"

```bash
pip install simple_NER
```

### "ovos-date-parser not found" warning

`TemporalNER` and `NumberNER` degrade gracefully but datetime/number extraction won't work.

```bash
pip install ovos-date-parser ovos-number-parser
```

### Permission denied

```bash
pip install --user simple_NER
```

---

## Usage Questions

### Q: How do I extract custom entity types?

```python
from simple_NER.rules import RuleNER

ner = RuleNER()
ner.add_rule("product", "I want {product}")
for ent in ner.extract_entities("I want iphone"):
    print(ent.value)  # iphone
```

### Q: How do I combine multiple annotators?

```python
from simple_NER.annotators.factory import create_pipeline

pipeline = create_pipeline(["email", "names", "locations"])
for ent in pipeline.process(text):
    print(ent.value, ent.entity_type)
```

### Q: How do I adjust confidence thresholds?

```python
from simple_NER.annotators.names_ner import NamesNER

ner = NamesNER(confidence_threshold=0.9)  # fewer, more confident
```

### Q: How do I get entity positions in text?

```python
for ent in entities:
    print(ent.value, ent.spans)  # e.g. [(8, 24)]
```

### Q: How do I export results?

```python
import json
data = {"text": text, "entities": [e.as_json() for e in entities]}
with open("results.json", "w") as f:
    json.dump(data, f, indent=2)
```

---

## Performance

### Slow on large files

```python
from simple_NER.utils.batch import BatchProcessor
processor = BatchProcessor(pipeline, batch_size=100)
results = processor.process_batch(texts, use_multiprocessing=True)
```

### High memory usage

Use streaming — process one text at a time without storing all results:

```python
from simple_NER.utils.batch import StreamingProcessor
for text, entities in StreamingProcessor(pipeline).process_stream(gen()):
    handle(entities)
```

### Repeated queries on same text

```python
from simple_NER.utils.cache import LRUCache
cache = LRUCache(max_size=1000)
entities = cache.get(text) or cache.set(text, pipeline.process(text)) or cache.get(text)
```

---

## Error Messages

### "ValueError: Unknown annotator: xyz"

```python
from simple_NER.annotators.factory import list_available_annotators
print(list_available_annotators())  # check exact key names
```

### "RuntimeWarning: coroutine was never awaited"

```python
# use await or asyncio.run()
entities = await pipeline.process_async(text)
# or
entities = asyncio.run(pipeline.process_async(text))
```

---

## Known Limitations

- Most annotators are **English-only** (see language support Q above).
- `LocationNER` is **case-sensitive** by default; pass `lowercase=True` to disable.
- Overlapping spans: use `dedup_strategy="keep_longest"` in `NERPipeline`.
- Rule-based extraction only matches patterns you define — add more rules for more variation.

---

## Getting Help

- [README](../readme.md) — quick start
- [API Reference](API.md)
- [Tutorials](TUTORIALS.md)
- [Issues](https://github.com/OpenJarbas/simple_NER/issues)

---

## Version History

| Version | Notes |
|---------|-------|
| 0.9.0 | Major refactor: async, caching, CLI, 16 annotators, OVOS plugin |
| 0.8.1 | Type hints, linting, tests |
| 0.4.x | Original release |
