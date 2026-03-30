# Tutorials

Step-by-step tutorials for common simple_NER use cases.

## Table of Contents

- [Tutorial 1: Getting Started](#tutorial-1-getting-started)
- [Tutorial 2: Building a Pipeline](#tutorial-2-building-a-pipeline)
- [Tutorial 3: Custom Annotators](#tutorial-3-custom-annotators)
- [Tutorial 4: Processing Large Datasets](#tutorial-4-processing-large-datasets)
- [Tutorial 5: Async Processing](#tutorial-5-async-processing)
- [Tutorial 6: Caching Results](#tutorial-6-caching-results)

---

## Tutorial 1: Getting Started

**Goal:** Extract entities from text in 5 minutes.

### Step 1: Install

```bash
pip install simple_NER
```

### Step 2: Basic Extraction

```python
from simple_NER.annotators.factory import create_pipeline

# Create pipeline with common annotators
pipeline = create_pipeline(["email", "names", "locations"])

# Extract entities
text = "John Doe lives in Lisbon. Contact: john@example.com"
entities = pipeline.process(text)

# Display results
print(f"Found {len(entities)} entities:")
for ent in entities:
    print(f"  • {ent.value} ({ent.entity_type})")
```

**Output:**
```
Found 3 entities:
  • john@example.com (email)
  • John Doe (Noun)
  • Lisbon (Capital City)
```

### Step 3: Export Results

```python
import json

# Export to JSON
data = {
    "text": text,
    "entities": [ent.as_json() for ent in entities]
}

with open("results.json", "w") as f:
    json.dump(data, f, indent=2)
```

### Exercise

Try extracting entities from your own text! Modify the `text` variable and run again.

---

## Tutorial 2: Building a Pipeline

**Goal:** Combine multiple annotators with custom deduplication.

### Step 1: Import Components

```python
from simple_NER.pipeline import NERPipeline
from simple_NER.annotators.email_ner import EmailAnnotator
from simple_NER.annotators.names_ner import NamesNER
from simple_NER.annotators.locations_ner import LocationNER
```

### Step 2: Create Annotators

```python
email_ner = EmailAnnotator()
names_ner = NamesNER(confidence_threshold=0.75)
location_ner = LocationNER(
    include_countries=True,
    include_capitals=True,
    include_cities=False
)
```

### Step 3: Build Pipeline

```python
pipeline = NERPipeline(
    annotators=[email_ner, names_ner, location_ner],
    dedup_strategy="keep_higher_confidence"
)
```

### Step 4: Process Text

```python
text = "Dr. Alice Smith from MIT in Cambridge published research."
text += " Contact: alice@mit.edu"

entities = pipeline.process(text)

for ent in entities:
    print(f"{ent.value:20} -> {ent.entity_type:15} (conf: {ent.confidence:.2f})")
```

### Step 5: Compare Deduplication Strategies

```python
texts = ["John at john@example.com"]
strategies = ["keep_all", "keep_longest", "keep_higher_confidence", "keep_first"]

for strategy in strategies:
    p = NERPipeline([email_ner, names_ner], dedup_strategy=strategy)
    results = p.process(texts[0])
    print(f"{strategy:25}: {len(results)} entities")
```

### Exercise

Experiment with different deduplication strategies. Which works best for your use case?

---

## Tutorial 3: Custom Annotators

**Goal:** Create a custom annotator for URLs.

### Step 1: Create Annotator Class

```python
from simple_NER.annotators.base import BaseAnnotator
from simple_NER import Entity
import re

class URLAnnotator(BaseAnnotator):
    """Extract URLs from text."""
    
    URL_PATTERN = re.compile(
        r'https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)', 
        re.IGNORECASE
    )
    
    @property
    def name(self) -> str:
        return "url"
    
    def annotate(self, text: str):
        for match in self.URL_PATTERN.finditer(text):
            yield Entity(
                value=match.group(),
                entity_type="url",
                source_text=text,
                confidence=0.9,
                data={"start": match.start(), "end": match.end()}
            )
```

### Step 2: Test Annotator

```python
url_ner = URLAnnotator()
text = "Visit https://example.com or http://test.org/page"

for ent in url_ner.extract_entities(text):
    print(f"Found URL: {ent.value}")
```

### Step 3: Add to Pipeline

```python
from simple_NER.pipeline import NERPipeline
from simple_NER.annotators.email_ner import EmailAnnotator

pipeline = NERPipeline([URLAnnotator(), EmailAnnotator()])

text = "Contact john@example.com or visit https://example.com"
entities = pipeline.process(text)

for ent in entities:
    print(f"{ent.value} -> {ent.entity_type}")
```

### Step 4: Register with Factory

```python
from simple_NER.annotators.factory import register_annotator

register_annotator("url", URLAnnotator)

# Now you can use factory
from simple_NER.annotators.factory import get_annotator

url_ner = get_annotator("url")
```

### Exercise

Create a custom annotator for phone numbers or hashtags.

---

## Tutorial 4: Processing Large Datasets

**Goal:** Efficiently process thousands of texts.

### Step 1: Setup Batch Processor

```python
from simple_NER.pipeline import NERPipeline
from simple_NER.utils.batch import BatchProcessor

pipeline = create_pipeline(["email", "names"])
processor = BatchProcessor(pipeline, batch_size=100)
```

### Step 2: Define Progress Callback

```python
def progress_callback(current, total):
    percent = (current / total) * 100
    print(f"\rProcessing: {current}/{total} ({percent:.1f}%)", end="")
```

### Step 3: Process Batch

```python
# Generate sample texts
texts = [f"Contact user{i}@example.com for info" for i in range(1000)]

# Process with progress tracking
results = processor.process_batch(
    texts,
    use_multiprocessing=True,
    progress_callback=progress_callback
)

print(f"\nProcessed {len(results)} texts")
print(f"Total entities: {sum(len(r) for r in results)}")
```

### Step 4: Stream Processing

For very large files, use streaming:

```python
from simple_NER.utils.batch import StreamingProcessor

stream_processor = StreamingProcessor(pipeline, buffer_size=10)

def file_generator(filepath):
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield line

for text, entities in stream_processor.process_stream(file_generator("large_file.txt")):
    # Process each result immediately
    print(f"{len(entities)} entities in: {text[:50]}...")
```

### Step 5: Save Results Incrementally

```python
import json

with open("results.jsonl", "w") as f:
    for text, entities in stream_processor.process_stream(file_generator("input.txt")):
        result = {
            "text": text,
            "entities": [e.as_json() for e in entities]
        }
        f.write(json.dumps(result) + "\n")
```

### Exercise

Process a large text file using streaming. Measure memory usage vs batch processing.

---

## Tutorial 5: Async Processing

**Goal:** Use async/await for concurrent processing.

### Step 1: Import Async Components

```python
import asyncio
from simple_NER.pipeline import AsyncNERPipeline
from simple_NER.annotators.email_ner import EmailAnnotator
from simple_NER.annotators.names_ner import NamesNER
```

### Step 2: Create Async Pipeline

```python
pipeline = AsyncNERPipeline([EmailAnnotator(), NamesNER()])
```

### Step 3: Process Single Text

```python
async def process_single():
    entities = await pipeline.process_async("John at john@example.com")
    print(f"Found {len(entities)} entities")

asyncio.run(process_single())
```

### Step 4: Process Batch Concurrently

```python
async def process_batch():
    texts = [
        "John at john@example.com",
        "Alice at alice@test.org",
        "Bob at bob@company.com",
    ]
    
    results = await pipeline.process_batch_async(texts, max_concurrency=2)
    
    for text, entities in zip(texts, results):
        print(f"{text}: {len(entities)} entities")

asyncio.run(process_batch())
```

### Step 5: Process with Rate Limiting

```python
async def process_with_rate_limit(texts, max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_one(text):
        async with semaphore:
            return await pipeline.process_async(text)
    
    tasks = [process_one(text) for text in texts]
    return await asyncio.gather(*tasks)

texts = [f"Email user{i}@example.com" for i in range(100)]
results = asyncio.run(process_with_rate_limit(texts))
```

### Exercise

Compare async vs sync processing speed for 100 texts.

---

## Tutorial 6: Caching Results

**Goal:** Cache NER results to avoid re-processing.

### Step 1: LRU Cache (In-Memory)

```python
from simple_NER.utils.cache import LRUCache

cache = LRUCache(max_size=100)
```

### Step 2: Use Cache with Pipeline

```python
pipeline = create_pipeline(["email", "names"])

def process_with_cache(text):
    # Check cache first
    cached = cache.get(text)
    if cached is not None:
        print(f"[CACHE HIT] {text[:30]}...")
        return cached
    
    # Process and cache
    entities = pipeline.process(text)
    cache.set(text, entities)
    print(f"[CACHE MISS] {text[:30]}...")
    return entities

# First call - cache miss
entities1 = process_with_cache("Contact john@example.com")

# Second call - cache hit!
entities2 = process_with_cache("Contact john@example.com")

print(f"Cache stats: {cache.stats()}")
```

### Step 3: File Cache (Persistent)

```python
from simple_NER.utils.cache import FileCache

file_cache = FileCache(cache_dir=".ner_cache", max_size=1000)

# Same API as LRU cache
file_cache.set("text", entities)
entities = file_cache.get("text")

# Cache persists after program restart
```

### Step 4: Cache Warming

```python
# Pre-populate cache with common texts
common_texts = [
    "Contact support@example.com",
    "Email sales@company.org",
    "Reach out to info@test.com",
]

for text in common_texts:
    entities = pipeline.process(text)
    cache.set(text, entities)

print(f"Cache warmed with {cache.size} entries")
```

### Exercise

Implement a cache layer for your application. Measure speedup for repeated queries.

---

## Next Steps

After completing these tutorials:

1. **Explore Examples:** See `examples/` directory
2. **API Reference:** Read `docs/API.md`
3. **Build Something:** Create your own annotator!
4. **Contribute:** Share your annotator with the community

---

## Getting Help

- **Documentation:** `docs/` directory
- **Examples:** `examples/` directory
- **Issues:** https://github.com/OpenJarbas/simple_NER/issues
- **Discussions:** https://github.com/OpenJarbas/simple_NER/discussions
