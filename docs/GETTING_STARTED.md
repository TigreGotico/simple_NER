# Getting Started with simple_NER

Welcome! This guide walks you through installing, running, and using simple_NER for the first time.

## Installation

### Prerequisites
- Python 3.10 or later
- pip or uv package manager

### Quick Install

```bash
pip install simple_NER
```

Or with development tools:

```bash
pip install "simple_NER[dev]"
```

## Your First NER Pipeline

Here's the simplest example — extract email, phone, and dates from text:

```python
from simple_NER import create_pipeline

# Create a pipeline with specific entity types
pipe = create_pipeline(["email", "phone", "temporal"])

# Process some text
text = "Call me at +1-800-555-0100 or email john@example.com by 2025-06-01"

# Extract entities
for entity in pipe.process(text):
    print(f"{entity.entity_type:12} | {entity.value:20} | confidence: {entity.confidence}")
```

**Output:**
```
phone        | +1-800-555-0100      | confidence: 0.9
email        | john@example.com     | confidence: 1.0
date         | 2025-06-01           | confidence: 0.85
```

## Understanding Entity Objects

Each `Entity` contains:

- **value**: The extracted text
- **entity_type**: The label (e.g., `"email"`, `"phone"`)
- **confidence**: 0.0–1.0 (higher = more certain)
- **data**: Extra metadata specific to that entity type (e.g., for email: `local_part`, `domain`)
- **spans**: Character positions in the original text

```python
for entity in pipe.process(text):
    print(f"Found '{entity.value}' at position {entity.spans}")
    print(f"Extra data: {entity.data}")
```

## Common Annotator Types

| Type | What it finds | Example |
|:---|:---|:---|
| `email` | Email addresses | john@example.com |
| `phone` | Phone numbers | +1-800-555-0100 |
| `temporal` | Dates, times, durations | 2025-06-01, in 3 days |
| `numbers` | Numeric and written numbers | 42, seventy-three |
| `currency` | Money amounts | $99.99, 100 EUR |
| `locations` | Countries, cities, capitals | New York, France |
| `names` | Person names | John Smith, Mary Johnson |
| `organization` | Company names | Apple Inc, Google LLC |
| `url` | HTTP/HTTPS URLs | https://example.com |
| `hashtag` | #hashtags | #python, #NLP |

**See all 16 annotators:** [docs/index.md#all-annotators](index.md#all-annotators)

## Customizing Entity Confidence

Some annotators let you tweak how confident they need to be to return entities. For example, `LocationNER` can distinguish between cities and countries:

```python
from simple_NER import create_pipeline

pipe = create_pipeline(
    ["locations"],
    annotator_params={
        "locations": {
            "include_cities": True,
            "label_confidence": {
                "City": 0.7,      # Less strict for cities
                "Country": 0.95   # Very strict for countries
            }
        }
    }
)

for entity in pipe.process("Paris is in France"):
    print(entity.entity_type, entity.value, entity.confidence)
```

## Handling Overlapping Entities

When multiple annotators find overlapping text (e.g., both "5" as a number and as part of a date), the pipeline uses a **dedup strategy**:

```python
# Keep only the longest span
pipe = create_pipeline(["numbers", "temporal"], dedup_strategy="keep_longest")

# Keep the one with highest confidence
pipe = create_pipeline(["numbers", "temporal"], dedup_strategy="keep_higher_confidence")

# Keep all (no dedup)
pipe = create_pipeline(["numbers", "temporal"], dedup_strategy="keep_all")
```

## Async Processing (Batch Mode)

For processing many texts, use the async pipeline:

```python
import asyncio
from simple_NER.pipeline import AsyncNERPipeline

async def process_batch():
    pipe = AsyncNERPipeline()
    pipe.add_annotator("email")
    pipe.add_annotator("phone")
    
    texts = [
        "Email: alice@example.com",
        "Phone: +1-555-0100",
        "Both: bob@test.com and 555-1234",
    ]
    
    results = await pipe.process_batch_async(texts, max_concurrency=5)
    
    for text, entities in zip(texts, results):
        print(f"Text: {text}")
        for entity in entities:
            print(f"  - {entity.entity_type}: {entity.value}")

asyncio.run(process_batch())
```

## Multi-Language Support

Pass `lang` to the pipeline — it forwards to all annotators that support it:

```python
# German date and number parsing
pipe = create_pipeline(
    ["temporal", "numbers", "currency"],
    lang="de-de"
)

for entity in pipe.process("Das Datum ist 15.03.2025 und der Betrag ist 99,99 EUR"):
    print(entity.value, entity.entity_type)
```

**Languages supported per annotator:**
- `temporal`, `numbers`, `date`, `currency`, `organization` — see `docs/FAQ.md#Q-What-languages-are-supported` for details
- `locations`, `email`, `phone`, `url`, `hashtag` — language-agnostic

## Custom Entity Types

### Option 1: Simple Wordlist

```python
from simple_NER import create_pipeline

pipe = create_pipeline(["lookup"])

# Add words to recognize
pipe.annotators[0].add_wordlist("color", ["red", "blue", "green", "yellow"])

for entity in pipe.process("I like blue cars"):
    print(entity.value, entity.entity_type)  # blue  color
```

### Option 2: Regex Patterns

```python
from simple_NER.annotators.simple_ner import SimpleNER

ner = SimpleNER()
ner.add_entity_examples("color", ["red", "blue", "green"])

for entity in ner.extract_entities("the ball is bright red"):
    print(entity.value, entity.entity_type)  # red  color
```

## Next Steps

- **Deep dive:** [docs/index.md](index.md) — complete API reference
- **Tutorials:** [docs/TUTORIALS.md](TUTORIALS.md) — step-by-step guides
- **Examples:** [examples/README.md](../examples/README.md) — 15+ runnable scripts
- **FAQ:** [docs/FAQ.md](FAQ.md) — common questions answered
- **API Reference:** [docs/API.md](API.md) — class and method details

## Troubleshooting

### "Module not found" error

```bash
pip install simple_NER --upgrade
```

### Entity not being recognized

1. Check **confidence**: add `print(entity.confidence)` to see how certain the detector is
2. **Adjust parameters**: pass `annotator_params` to `create_pipeline` (see [Customizing Entity Confidence](#customizing-entity-confidence) above)
3. **Check language**: if using non-English text, pass `lang="de-de"` (or your language code)
4. **See examples:** browse [examples/](../examples/) for use cases similar to yours

### Performance slow on large batches

Use the **async pipeline** (see [Async Processing](#async-processing-batch-mode)) with `max_concurrency` tuned to your CPU cores.

## Need Help?

- **Questions?** Check [docs/FAQ.md](FAQ.md)
- **API details?** See [docs/API.md](API.md)
- **Working examples?** Browse [examples/README.md](../examples/README.md)
- **Found a bug?** Open an issue on [GitHub](https://github.com/OpenJarbas/simple_NER/issues)
