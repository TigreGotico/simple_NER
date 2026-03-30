# Migration Guide

This guide helps you migrate from older versions of simple_NER to the new architecture (v0.8+).

## What Changed in v0.8?

### 1. New Base Classes

**Before:**
```python
from simple_NER.annotators import NERWrapper

class MyAnnotator(NERWrapper):
    def __init__(self):
        super().__init__()
        self.add_detector(self.annotate)
    
    def annotate(self, text):
        # extraction logic
        yield Entity(...)
```

**After (recommended):**
```python
from simple_NER.annotators.base import BaseAnnotator

class MyAnnotator(BaseAnnotator):
    @property
    def name(self) -> str:
        return "my_annotator"
    
    def annotate(self, text: str):
        # extraction logic
        yield Entity(...)
```

**Benefits:**
- Cleaner interface
- Automatic `extract_entities()` implementation
- Consistent `name` property
- Built-in `confidence` attribute

---

### 2. Unified Annotators

Several annotators have been unified:

| Old Classes | New Class | Status |
|-------------|-----------|--------|
| `DateTimeNER`, `TimedeltaNER` | `TemporalNER` | ✅ Aliases maintained |
| `LocationNER`, `CitiesNER` | `LocationNER` | ✅ Alias maintained |

**Before:**
```python
from simple_NER.annotators.datetime_ner import DateTimeNER, TimedeltaNER

date_ner = DateTimeNER()
duration_ner = TimedeltaNER()
```

**After:**
```python
from simple_NER.annotators.temporal_ner import TemporalNER, DateTimeNER, TimedeltaNER

# Recommended
temporal_ner = TemporalNER()

# Still works (backward compatible)
date_ner = DateTimeNER()  # Alias
duration_ner = TimedeltaNER()  # Alias
```

---

### 3. New Factory Pattern

**Before:**
```python
from simple_NER.annotators.email_ner import EmailNER
from simple_NER.annotators.names_ner import NamesNER
from simple_NER.annotators import NERWrapper

wrapper = NERWrapper()
wrapper.add_detector(EmailNER().extract_entities)
wrapper.add_detector(NamesNER().extract_entities)
```

**After (recommended):**
```python
from simple_NER.annotators.factory import create_pipeline

pipeline = create_pipeline(["email", "names"])
entities = pipeline.process(text)
```

**Benefits:**
- Simpler configuration
- Automatic deduplication
- Easy to add/remove annotators

---

### 4. Pipeline with Deduplication

**Before:**
```python
# No built-in deduplication
wrapper = NERWrapper()
wrapper.add_detector(detector1)
wrapper.add_detector(detector2)
# Manual deduplication needed
```

**After:**
```python
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline(
    annotators=[annotator1, annotator2],
    dedup_strategy="keep_higher_confidence"  # or keep_all, keep_longest, keep_first
)
entities = pipeline.process(text)  # Automatic deduplication
```

---

### 5. Optional Dependencies

Some annotators now support multiple backends:

**TemporalNER:**
- Primary: `ovos-date-parser`
- Fallback: `lingua_nostra` (deprecated)

**NumberNER:**
- Primary: `ovos-number-parser`
- Fallback: `lingua_nostra` (deprecated)

**Before:**
```bash
pip install lingua_nostra
```

**After (recommended):**
```bash
pip install ovos-date-parser ovos-number-parser
```

---

## Step-by-Step Migration

### Step 1: Update Installation

```bash
# Install with new dependencies
pip install simple_NER[all,dev]

# Or install specific backends
pip install ovos-date-parser ovos-number-parser quantulum3
```

### Step 2: Update Imports

```python
# Old imports (still work)
from simple_NER.annotators.datetime_ner import DateTimeNER

# New imports (recommended)
from simple_NER.annotators.temporal_ner import TemporalNER
```

### Step 3: Update Custom Annotators

```python
# Old pattern
class MyAnnotator(NERWrapper):
    def __init__(self):
        super().__init__()
        self.add_detector(self.annotate)

# New pattern
class MyAnnotator(BaseAnnotator):
    @property
    def name(self) -> str:
        return "my_annotator"
```

### Step 4: Use Factory (Optional)

```python
# Instead of manual instantiation
from simple_NER.annotators.factory import get_annotator

email_ner = get_annotator("email")
names_ner = get_annotator("names")
```

### Step 5: Use Pipeline

```python
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline(
    [email_ner, names_ner],
    dedup_strategy="keep_higher_confidence"
)
```

---

## Compatibility Matrix

| Feature | Old API | New API | Status |
|---------|---------|---------|--------|
| `Entity` | ✅ | ✅ | Unchanged |
| `SimpleNER` | ✅ | ✅ | Unchanged |
| `RuleNER` | ✅ | ✅ | Unchanged |
| `RegexNER` | ✅ | ✅ | Improved (no shadowing) |
| `NeuralNER` | ✅ | ✅ | Improved (no shadowing) |
| `NERWrapper` | ✅ | ✅ | Still supported |
| `DateTimeNER` | ✅ | ⚠️ | Alias to TemporalNER |
| `TimedeltaNER` | ✅ | ⚠️ | Alias to TemporalNER |
| `CitiesNER` | ✅ | ⚠️ | Alias to LocationNER |
| `BaseAnnotator` | ❌ | ✅ | New |
| `NERPipeline` | ❌ | ✅ | New |
| Factory | ❌ | ✅ | New |

---

## Common Issues

### Issue 1: Missing ovos-date-parser

**Error:**
```
WARNING - Neither ovos-date-parser nor lingua_nostra available
```

**Solution:**
```bash
pip install ovos-date-parser ovos-number-parser
```

Or continue using lingua_nostra:
```bash
pip install lingua_nostra
```

---

### Issue 2: Annotator name not found

**Error:**
```
ValueError: Unknown annotator: email
```

**Solution:**
Make sure the factory module is imported:
```python
from simple_NER.annotators import factory  # Triggers auto-registration
email_ner = get_annotator("email")
```

---

### Issue 3: Custom annotator not working with factory

**Problem:**
```python
register_annotator("my_annotator", MyAnnotator)
get_annotator("my_annotator")  # Error
```

**Solution:**
Ensure your annotator inherits from `BaseAnnotator`:
```python
from simple_NER.annotators.base import BaseAnnotator

class MyAnnotator(BaseAnnotator):
    @property
    def name(self) -> str:
        return "my_annotator"
    
    def annotate(self, text):
        yield Entity(...)
```

---

## Getting Help

- **Documentation:** `docs/API.md`
- **Examples:** `examples/` directory
- **Issues:** https://github.com/OpenJarbas/simple_NER/issues
