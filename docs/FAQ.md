# FAQ & Troubleshooting

## General Questions

### Q: What is simple_NER?

**A:** A lightweight rule-based NER library. Extracts named entities via simplematch patterns, regex, and pre-built annotators for common entity types (email, names, locations, dates, numbers, etc.).

### Q: What entity types does it support?

**A:** 16 built-in annotators: email, names, locations (countries/capitals/cities), temporal (datetime/duration), numbers, lookup, URL, phone, currency, organization, hashtag, date. Custom types via `RuleNER` or `RegexNER`.

### Q: What Python versions are supported?

**A:** Python 3.10-3.13.

### Q: How does it compare to spaCy or NLTK?

**A:** simple_NER is lighter and rule-based: no ML models, no training data, easy to customize. spaCy/NLTK are better when statistical accuracy matters more than speed and interpretability.

### Q: What languages are supported?

**A:** Language support varies by annotator:

| Annotator | Language coverage |
|-----------|-------------------|
| `TemporalNER`, `NumberNER` | Multi-language via `ovos-date-parser` / `ovos-number-parser`, pass `lang="de-de"` or similar |
| `DateAnnotator` | Written month names in EN/ES/FR/DE/PT/IT/NL, numeric formats are language-agnostic |
| `CurrencyAnnotator` | Currency words in EN/ES/FR/DE/PT/IT/NL, symbols/ISO codes are language-agnostic |
| `OrganizationAnnotator` | Company suffixes for DE/FR/ES/PT/IT/NL/BE and English, accented Latin characters in the name regex |
| `HashtagAnnotator` | Fully Unicode-aware (`re.UNICODE`): matches hashtags in any script |

| Annotator | Language coverage |
|-----------|-------------------|
| `LocationNER` | Language-agnostic (bundled JSON city/country names) |
| `EmailAnnotator`, `URLAnnotator`, `PhoneAnnotator` | Language-agnostic (structural patterns) |
| `LookUpNER` | Per-language via `.entity` resource files under `res/<lang>/` |

Pass `lang` to any annotator or to `create_pipeline(names, lang="de-de")`: the factory forwards it to all constructors.

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

Use streaming: process one text at a time without storing all results:

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

### Q: How do I add phone number patterns for a new language?

**A:** Create `locale/<lang>/phone.rx` (one regex per line). `PhoneAnnotator` calls `BaseAnnotator._load_rx("phone", lang)` at init time and merges those patterns into its compiled set alongside the built-in `en-us` patterns.

### Q: How do I add currency phrases for a new language?

**A:** Create `locale/<lang>/currency.intent` with one simplematch template per line (e.g. `{amount} euros`). `CurrencyAnnotator` loads these via `BaseAnnotator._load_intents("currency", lang)` and converts them to regex via `intent_to_regex()`.

### Q: Does the pipeline handle overlapping entity spans?

**A:** Yes, since v0.9.0. `NERPipeline._deduplicate` applies a longest-span-wins strategy across all annotator types. When two entities overlap (e.g. `$500` matched as both `money` and `written_number`), only the entity with the larger span is kept. Exact-span duplicates with different labels are also de-duplicated.

### Q: Can I set different confidence per entity type in `LookUpNER`?

**A:** Yes. Pass `label_confidence={"City": 0.7, "Country": 0.95}` at construction time. Labels not listed fall back to the global `confidence` parameter. Same interface applies to `LocationNER`.

---

## Known Limitations

- Most annotators are **English-only** (see language support Q above).
- `LocationNER` is case-sensitive by default. Pass `lowercase=True` to disable it.
- Overlapping spans: use `dedup_strategy="keep_longest"` in `NERPipeline`.
- Rule-based extraction only matches patterns you define: add more rules for more variation.

---

## Getting Help

- [README](../readme.md): quick start
- [API Reference](API.md)
- [Tutorials](TUTORIALS.md)
- [Issues](https://github.com/TigreGotico/simple_NER/issues)

### Q: How do I use HuggingFace datasets for entity extraction?

**A:** simple_NER integrates with **ahocorasick-ner**, which provides fast multi-entity matching via pre-built HuggingFace dataset loaders. Install the optional dependency:

```bash
pip install "ahocorasick-ner[datasets]"
```

Then use dataset NER classes in a simple_NER pipeline:

```python
from ahocorasick_ner.datasets import WikidataEntityNER, BC5CDRMedicalNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()

# Extract animals from Wikidata
animals = WikidataEntityNER(entity_type="Animal", wikidata_qid="Q729")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(animals))

# Extract diseases from biomedical literature
diseases = BC5CDRMedicalNER(entity_type="Disease")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(diseases))

for entity in pipeline.process("Dogs can get arthritis and heart disease"):
    print(entity.entity_type, entity.value)
# Animal  Dogs
# Disease arthritis
# Disease heart disease
```

**Available dataset loaders** (in ahocorasick-ner):

**Wikidata Entities (easy-access subclasses: no QID needed):**

- `WikidataAnimalNER`: animals (1M+ names, all languages)
- `WikidataPlantNER`: plants (500k+ names)
- `WikidataCountryNER`: countries (195 names)
- `WikidataCityNER`: cities (worldwide)

- `WikidataPersonNER`: person names (100M+ from Q5)
- `WikidataProfessionNER`: professions/occupations
- `WikidataDiseaseNER`: diseases and medical conditions
- `WikidataLanguageNER`: languages of the world

- `WikidataSportNER`: sports and athletic activities
- `WikidataBodyPartNER`: anatomical body parts
- `WikidataFamilyRelationNER`: family relationships
- **Or generic**: `WikidataEntityNER(entity_type="...", wikidata_qid="...")` for custom QIDs

**Names & Locations:**
- `PersonNamesNER`: person surnames (30+ countries/languages)
- `GeoNamesNER`: 280k+ cities and locations worldwide

**Generic HuggingFace datasets:**
- `GenericHFDatasetNER`: any HF dataset with entities in a column
- `BC5CDRMedicalNER`: diseases and chemicals from biomedical NER

**Media & Entertainment (Jarbas/TigreGotico):**

- `MovieActorNER`: 6.3M movie actor names
- `MovieDirectorNER`: 128k movie director names
- `MovieComposerNER`: 221k movie composer names
- `MetalArchivesBandsNER`: 4.6k metal band names

- `MetalArchivesTrackNER`: 205k metal tracks + albums
- `JazzNER`: jazz artists and genres
- `ProgRockNER`: prog rock artists and genres
- `MusicNER`: comprehensive music dataset (all genres combined)

- `EncyclopediaMetallvmNER`, `ImdbNER`: pre-built combined datasets

See [`ahocorasick-ner` docs](https://github.com/TigreGotico/ahocorasick-ner) for full list.

### Q: How do I filter datasets to extract only specific entities?

**A:** Many dataset loaders support filtering by column values. This reduces the automaton size and improves matching speed.

**Supported loaders:**
- `MetalArchivesBandsNER(origin="Portugal")`: metal bands from a country
- `MetalArchivesTrackNER(band_origin="Sweden")`: tracks from bands in a country
- `SpotifyTracksNER(genre="rock")`: tracks from a genre
- `GenericHFDatasetNER(..., filter_column="col", filter_value="val")`: any HF dataset

**Example:**
```python
from ahocorasick_ner.datasets import MetalArchivesBandsNER, SpotifyTracksNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()

# Only Portuguese bands
pt_bands = MetalArchivesBandsNER(origin="Portugal")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(pt_bands))

# Only rock tracks
rock = SpotifyTracksNER(genre="rock")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(rock))

for entity in pipeline.process("Moonspell and Queen"):
    print(entity.entity_type, entity.value)
# metal_band Moonspell
# track_name (Queen songs if available in rock)
```

**Benefits:**
- 50-90% smaller automaton (less memory)
- Faster matching on domain-specific data
- Semantic clarity (fewer false positives)

See [DATASET_INTEGRATION.md](DATASET_INTEGRATION.md#dataset-filtering-selective-loading) for more examples.

---

## Version History

| Version | Notes |
|---------|-------|
| 0.9.0 | Major refactor: async, caching, CLI, 16 annotators, OVOS plugin |
| 0.8.1 | Type hints, linting, tests |
| 0.4.x | Original release |

---

## Q: How do I integrate HuggingFace dataset taggers into a pipeline?

Use `AhocorasickAnnotatorWrapper` from `simple_NER.annotators.ahocorasick_wrapper`:

```python
from ahocorasick_ner.datasets import WikidataAnimalNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAnimalNER()))
for entity in pipeline.process("I saw a dog and a cat"):
    print(entity.entity_type, entity.value)
```

See [DATASET_INTEGRATION.md](DATASET_INTEGRATION.md) for the full guide.

---

## Q: Why does `NamesNER` miss names at the start of a sentence?

By design. Single capitalized words at sentence boundaries (position 0, or after `.!?`) score 0.55 confidence. This is below the default threshold of 0.65, so it suppresses false positives like "Send" or "Meeting". Multi-word names ("John Doe") always score 0.85 regardless of position. Lower `confidence_threshold` to capture sentence-initial single names if needed:

```python
ner = NamesNER(confidence_threshold=0.5)
```

---
[← Getting Started](GETTING_STARTED.md) · [Home](README.md) · [API Reference →](API.md)
