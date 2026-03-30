# Simple NER

[![PyPI - Version](https://img.shields.io/pypi/v/simple_NER.svg)](https://pypi.org/project/simple_NER/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/simple_NER.svg)](https://pypi.org/project/simple_NER/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/OpenJarbas/simple_NER/build_tests.yml)](https://github.com/OpenJarbas/simple_NER/actions)
[![License](https://img.shields.io/github/license/OpenJarbas/simple_NER.svg)](https://github.com/OpenJarbas/simple_NER/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-88%20passed-green)](https://github.com/OpenJarbas/simple_NER/actions)

**Simple NER** is a flexible, modular named entity recognition (NER) library for Python. It provides multiple extraction methods including rule-based patterns, regex, and pre-built annotators for common entity types.

## ✨ Features

- 🔧 **Rule-based NER** - Pattern matching with simplematch syntax
- 🔍 **Regex NER** - Custom regex patterns for flexible extraction
- 📦 **Built-in Annotators** - 16 pre-built entity extractors
- 🚀 **Pipeline System** - Multiple annotators with deduplication
- 🏭 **Factory Pattern** - Create annotators by name
- ⚡ **Async Support** - Concurrent processing for I/O-bound tasks
- 💾 **Caching** - LRU and file-based result caching
- 📊 **Visualization** - Terminal colors, HTML, and table output
- 🖥️ **CLI Tool** - Command-line interface for quick extraction
- 🧪 **Well Tested** - 88+ unit tests
- 🎯 **Lightweight** - Only 4 core dependencies

## 📦 Installation

### Basic Installation

```bash
pip install simple_NER
```

**That's it!** Only 4 core dependencies including OVOS backends.

### Development Setup

```bash
pip install simple_NER[dev]
```

## 🚀 Quick Start

### 5-Minute Tutorial

```python
from simple_NER.annotators.factory import create_pipeline

# Create a pipeline with multiple annotators
pipeline = create_pipeline(["email", "names", "locations"])

# Extract entities
text = "John Doe lives in Lisbon. Contact: john@example.com"
entities = pipeline.process(text)

# Display results
for ent in entities:
    print(f"{ent.value} -> {ent.entity_type}")
```

**Output:**
```
john@example.com -> email
John Doe -> Noun
Lisbon -> Capital City
```

### Using Individual Annotators

```python
from simple_NER.annotators.email_ner import EmailNER

ner = EmailNER()
for ent in ner.extract_entities("Contact support@company.com"):
    print(f"Found: {ent.value} ({ent.entity_type})")
# Found: support@company.com (email)
```

### Using Rule-Based NER

```python
from simple_NER.rules import RuleNER

ner = RuleNER()
ner.add_rule("name", "my name is {person}")

for ent in ner.extract_entities("my name is Alice"):
    print(f"Found: {ent.value} ({ent.entity_type})")
# Found: Alice (person)
```

## 📖 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Core Concepts](#-core-concepts)
- [Built-in Annotators](#-built-in-annotators)
- [Pipeline System](#-pipeline-system)
- [Factory Pattern](#-factory-pattern)
- [Advanced Features](#-advanced-features)
- [CLI Tool](#-cli-tool)
- [Examples](#-examples)
- [API Reference](#-api-reference)
- [Migration Guide](#-migration-guide)
- [FAQ](#-faq)

---

## 🎯 Core Concepts

### Entity

The fundamental data structure representing an extracted entity:

```python
from simple_NER import Entity

entity = Entity(
    value="john@example.com",
    entity_type="email",
    source_text="Contact john@example.com",
    confidence=1.0,
    data={"domain": "example.com"}
)

print(entity.value)          # "john@example.com"
print(entity.entity_type)    # "email"
print(entity.confidence)     # 1.0
print(entity.spans)          # [(8, 24)]
print(entity.as_json())      # Dict representation
```

### Annotator

An annotator extracts entities from text. All annotators follow the same interface:

```python
from simple_NER.annotators.base import BaseAnnotator
from simple_NER import Entity

class MyAnnotator(BaseAnnotator):
    @property
    def name(self) -> str:
        return "my_annotator"
    
    def annotate(self, text: str):
        if "hello" in text.lower():
            yield Entity("hello", "greeting", source_text=text)
```

### Pipeline

Combine multiple annotators with automatic deduplication:

```python
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline(
    annotators=[email_ner, names_ner],
    dedup_strategy="keep_higher_confidence"
)
```

---

## 📚 Built-in Annotators

### Email Extraction

```python
from simple_NER.annotators.email_ner import EmailNER

ner = EmailNER()
text = "Contact support@example.com or sales@company.org"

for ent in ner.extract_entities(text):
    print(f"{ent.value} -> {ent.entity_type}")
# support@example.com -> email
# sales@company.org -> email
```

### Name Extraction

```python
from simple_NER.annotators.names_ner import NamesNER

ner = NamesNER(confidence_threshold=0.8)
text = "John Doe met Alice Smith in Paris"

for ent in ner.extract_entities(text):
    print(f"{ent.value} -> {ent.entity_type} (conf: {ent.confidence})")
# John Doe -> Noun (conf: 0.80)
# Alice Smith -> Noun (conf: 0.80)
# Paris -> Noun (conf: 0.80)
```

### Location Extraction

```python
from simple_NER.annotators.locations_ner import LocationNER

ner = LocationNER(
    include_countries=True,
    include_capitals=True,
    include_cities=True
)

text = "Lisbon is the capital of Portugal"
for ent in ner.extract_entities(text):
    print(f"{ent.value} -> {ent.entity_type}")
# Lisbon -> Capital City
# Portugal -> Country
```

### Datetime & Duration

```python
from simple_NER.annotators.temporal_ner import TemporalNER

ner = TemporalNER()

# Datetime
for ent in ner.extract_entities("meeting tomorrow at 3pm"):
    if ent.entity_type == "relative_date":
        print(f"{ent.value} -> {ent.data['isoformat']}")

# Duration
for ent in ner.extract_entities("wait 5 minutes"):
    if ent.entity_type == "duration":
        print(f"{ent.value} -> {ent.data['total_seconds']} seconds")
```

### Written Numbers

```python
from simple_NER.annotators.numbers_ner import NumberNER

ner = NumberNER()
text = "I have three hundred apples"

for ent in ner.extract_entities(text):
    print(f"{ent.value} -> {ent.data['number']}")
# three hundred -> 300.0
```

### Complete Annotator List

| Name | Class | Description |
|------|-------|-------------|
| `email` | EmailAnnotator | Email addresses |
| `names` | NamesNER | Proper nouns |
| `locations` | LocationNER | Countries, capitals, cities |
| `temporal` | TemporalNER | Datetime and duration |
| `numbers` | NumberNER | Written numbers |
| `lookup` | LookUpNER | Wordlist lookup |
| `url`, `urls` | URLAnnotator | HTTP/HTTPS URLs ✨ NEW |
| `phone`, `phone_number` | PhoneAnnotator | Phone numbers ✨ NEW |
| `currency`, `money` | CurrencyAnnotator | Money/currency values ✨ NEW |
| `organization`, `org`, `company` | OrganizationAnnotator | Companies, universities ✨ NEW |
| `hashtag` | HashtagAnnotator | Social media hashtags ✨ NEW |
| `date` | DateAnnotator | Explicit calendar dates ✨ NEW |

---

## 🔌 OVOS Integration

simple_NER ships an **Intent Transformer** plugin for [OpenVoiceOS](https://github.com/OpenVoiceOS).
It runs after intent matching and injects extracted entities into `intent.match_data` so skill
handlers receive them without running NER themselves.

**Plugin type**: `opm.transformer.intent`
**Plugin ID**: `simple-ner-transformer`

### mycroft.conf

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

### How it works

```python
# After intent matching, intent.match_data is enriched:
# {"email": "john@example.com", "location": "Lisbon", ...}
# Existing keys are never overwritten.
```

The entity type → `match_data` key mapping is defined in `simple_NER/opm.py:_TYPE_MAP`.

---

## 🔧 Pipeline System

### Basic Pipeline

```python
from simple_NER.pipeline import NERPipeline
from simple_NER.annotators.email_ner import EmailAnnotator
from simple_NER.annotators.names_ner import NamesNER

pipeline = NERPipeline([
    EmailAnnotator(),
    NamesNER()
])

entities = pipeline.process("John at john@example.com")
```

### Deduplication Strategies

```python
# Keep all entities (no deduplication)
pipeline = NERPipeline(annotators, dedup_strategy="keep_all")

# Keep longest entity when spans overlap
pipeline = NERPipeline(annotators, dedup_strategy="keep_longest")

# Keep entity with higher confidence
pipeline = NERPipeline(annotators, dedup_strategy="keep_higher_confidence")

# Keep first detected entity
pipeline = NERPipeline(annotators, dedup_strategy="keep_first")
```

### Async Pipeline

```python
import asyncio
from simple_NER.pipeline import AsyncNERPipeline

async def main():
    pipeline = AsyncNERPipeline([email_ner, names_ner])
    
    # Single text
    entities = await pipeline.process_async("John at john@example.com")
    
    # Batch processing
    texts = ["text1", "text2", "text3"]
    results = await pipeline.process_batch_async(texts)

asyncio.run(main())
```

---

## 🏭 Factory Pattern

### Create Annotators by Name

```python
from simple_NER.annotators.factory import get_annotator, create_pipeline

# Single annotator
email_ner = get_annotator("email")
names_ner = get_annotator("names", confidence=0.9)

# Pipeline
pipeline = create_pipeline(
    ["email", "names", "locations"],
    dedup_strategy="keep_higher_confidence"
)

# List available
from simple_NER.annotators.factory import list_available_annotators
print(list_available_annotators())
# ['cities', 'countries', 'email', 'names', ...]
```

### Register Custom Annotator

```python
from simple_NER.annotators.factory import register_annotator
from simple_NER.annotators.base import BaseAnnotator

class MyAnnotator(BaseAnnotator):
    @property
    def name(self) -> str:
        return "my_annotator"
    
    def annotate(self, text):
        # Your logic here
        pass

register_annotator("my_annotator", MyAnnotator)
```

---

## ⚡ Advanced Features

### Caching

```python
from simple_NER.utils.cache import LRUCache, FileCache

# In-memory LRU cache
cache = LRUCache(max_size=100)
cache.set("text", entities)
entities = cache.get("text")
print(cache.stats())  # {'size': 1, 'hits': 0, 'misses': 1, ...}

# File-based cache
file_cache = FileCache(cache_dir=".ner_cache")
file_cache.set("text", entities)
entities = file_cache.get("text")
```

### Batch Processing

```python
from simple_NER.utils.batch import BatchProcessor

processor = BatchProcessor(pipeline, batch_size=100)

def progress(current, total):
    print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")

results = processor.process_batch(
    texts,
    use_multiprocessing=True,
    progress_callback=progress
)
```

### Streaming

```python
from simple_NER.utils.batch import StreamingProcessor

processor = StreamingProcessor(pipeline)

def text_generator():
    for line in open("large_file.txt"):
        yield line

for text, entities in processor.process_stream(text_generator()):
    print(f"{text}: {len(entities)} entities")
```

### Visualization

```python
from simple_NER.utils.visualization import (
    visualize_text_terminal,
    visualize_text_html,
    visualize_entities_table,
    print_colored_entities
)

# Terminal with colors
print(visualize_text_terminal(text, entities))

# HTML for web display
html = visualize_text_html(text, entities)

# Table format
print(visualize_entities_table(entities))

# Colored output
print_colored_entities(entities)
```

---

## 🖥️ CLI Tool

### Basic Usage

```bash
# Extract from text
python -m simple_NER.cli "John lives in Lisbon"

# Specific annotators
python -m simple_NER.cli "Email: test@example.com" -a email

# JSON output
python -m simple_NER.cli "text" --format json

# CSV output
python -m simple_NER.cli "text" --format csv
```

### File Processing

```bash
# Process file
python -m simple_NER.cli --file input.txt --output results.json

# With specific annotators
python -m simple_NER.cli -f input.txt -a email,names --format json
```

### Read from stdin

```bash
echo "Contact john@example.com" | python -m simple_NER.cli
cat file.txt | python -m simple_NER.cli --format json
```

### Options

```
-a, --annotators     Comma-separated list (default: email,names,locations)
-f, --file          Input file path
-o, --output        Output file path
--format            text, json, or csv
--dedup             Deduplication strategy
--spans             Show character spans
--list-annotators   List available annotators
--help              Show help message
```

---

## 📝 Examples

### Complete Example

```python
from simple_NER.annotators.factory import create_pipeline
from simple_NER.utils.visualization import visualize_text_terminal

# Create pipeline
pipeline = create_pipeline(["email", "names", "locations", "temporal"])

# Process text
text = """
Dr. Alice Smith from MIT in Cambridge will present on December 5th.
Contact: alice@mit.edu or call 555-123-4567.
The research spans three years with $2.5M funding.
"""

entities = pipeline.process(text)

# Display
print(f"Found {len(entities)} entities:")
for ent in entities:
    print(f"  {ent.value:20} -> {ent.entity_type}")

# Visualize
print(visualize_text_terminal(text, entities))

# Export
import json
with open("results.json", "w") as f:
    json.dump({
        "text": text,
        "entities": [e.as_json() for e in entities]
    }, f, indent=2)
```

### Custom Annotator

```python
from simple_NER.annotators.base import BaseAnnotator
from simple_NER import Entity
import re

class URLAnnotator(BaseAnnotator):
    URL_PATTERN = re.compile(r'https?://\S+')
    
    @property
    def name(self) -> str:
        return "url"
    
    def annotate(self, text: str):
        for match in self.URL_PATTERN.finditer(text):
            yield Entity(
                match.group(),
                "url",
                source_text=text,
                confidence=0.9
            )

# Use it
from simple_NER.pipeline import NERPipeline
from simple_NER.annotators.email_ner import EmailAnnotator

pipeline = NERPipeline([URLAnnotator(), EmailAnnotator()])
entities = pipeline.process("Visit https://example.com or email test@example.com")
```

---

## 📚 API Reference

Full API documentation is available in [`docs/API.md`](docs/API.md).

### Core Classes

- [`Entity`](docs/API.md#entity) - Entity data structure
- [`SimpleNER`](docs/API.md#simplener) - Base NER class
- [`RuleNER`](docs/API.md#rulener) - Rule-based extraction
- [`RegexNER`](docs/API.md#regexner) - Regex extraction

### Annotators

- [`BaseAnnotator`](docs/API.md#baseannotator) - Base class for annotators
- [`EmailAnnotator`](docs/API.md#emailannotator) - Email extraction
- [`NamesNER`](docs/API.md#namesner) - Name extraction
- [`LocationNER`](docs/API.md#locationner) - Location extraction
- [`TemporalNER`](docs/API.md#temporalner) - Datetime/duration
- [`NumberNER`](docs/API.md#numberner) - Written numbers
- [`KeywordNER`](docs/API.md#keywordner) - Keyword extraction
- [`UnitsNER`](docs/API.md#unitsner) - Unit extraction

### Pipeline

- [`NERPipeline`](docs/API.md#nerpipeline) - Sync pipeline
- [`AsyncNERPipeline`](docs/API.md#asyncnerpipeline) - Async pipeline

### Utilities

- [`LRUCache`](docs/API.md#lrucache) - In-memory cache
- [`FileCache`](docs/API.md#filecache) - File-based cache
- [`BatchProcessor`](docs/API.md#batchprocessor) - Batch processing
- [`StreamingProcessor`](docs/API.md#streamingprocessor) - Streaming

---

## 🔄 Migration Guide

### From Old Versions

**Old (v0.4.x):**
```python
from simple_NER.annotators.datetime_ner import DateTimeNER
ner = DateTimeNER()
```

**New (v0.9.x):**
```python
from simple_NER.annotators.temporal_ner import TemporalNER
ner = TemporalNER()  # DateTimeNER still works (alias)
```

### Using Factory (Recommended)

```python
from simple_NER.annotators.factory import get_annotator

# Instead of importing each class
email_ner = get_annotator("email")
names_ner = get_annotator("names")
locations_ner = get_annotator("locations")
```

Full migration guide: [`docs/MIGRATION.md`](docs/MIGRATION.md)

---

## ❓ FAQ

### Q: How do I add a custom entity type?

```python
from simple_NER.rules import RuleNER

ner = RuleNER()
ner.add_rule("product", "I want {product}")
ner.add_rule("product", "buy {product}")

for ent in ner.extract_entities("I want iphone"):
    print(ent.value)  # iphone
```

### Q: Can I use multiple languages?

Yes! Some annotators support language selection:

```python
from simple_NER.annotators.keyword_ner import KeywordNER

ner = KeywordNER(lang="en")  # or "pt", "es", etc.
```

### Q: How do I improve accuracy?

1. **Combine multiple annotators** in a pipeline
2. **Adjust confidence thresholds**
3. **Use domain-specific rules**
4. **Add custom wordlists**

### Q: Is it thread-safe?

Yes, annotators can be used in multiple threads. For async, use `AsyncNERPipeline`.

### Q: How do I handle large files?

Use streaming:

```python
from simple_NER.utils.batch import StreamingProcessor

processor = StreamingProcessor(pipeline)
for text, entities in processor.process_file("large.txt"):
    process(entities)
```

---

## 🤝 Contributing

Contributions are welcome! See our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Fork and clone
git clone https://github.com/your-username/simple_NER.git
cd simple_NER

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev,all]"

# Run tests
pytest test/ -v

# Install pre-commit hooks
pre-commit install
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Padaos](https://github.com/MycroftAI/padaos) - Pattern matching
- [OVOS](https://github.com/OpenVoiceOS) - Language parsing
- [Quantulum3](https://github.com/nielstron/quantulum3) - Unit extraction
- [RAKE](https://github.com/aneesha/RAKE) - Keyword extraction

---

## 📞 Support

- **Documentation:** [docs/](docs/)
- **Examples:** [examples/](examples/)
- **Issues:** https://github.com/OpenJarbas/simple_NER/issues
- **Discussions:** https://github.com/OpenJarbas/simple_NER/discussions
