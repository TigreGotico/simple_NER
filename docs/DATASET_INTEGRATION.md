# HuggingFace Dataset Integration

Complete guide to using HuggingFace datasets with simple_NER via ahocorasick-ner.

## Overview

simple_NER provides a pipeline adapter (`AhocorasickAnnotatorWrapper`) that integrates with **ahocorasick-ner**'s dataset loaders. This gives you access to **1.5B+ pre-built entities** from various sources.

```python
from ahocorasick_ner.datasets import WikidataAnimalNER, MovieActorNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

# Create pipeline
pipeline = NERPipeline()

# Add dataset-backed entity taggers
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAnimalNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(MovieActorNER()))

# Extract
for entity in pipeline.process("A dog starring Tom Hanks"):
    print(entity.entity_type, entity.value)
```

---

## Installation

```bash
# With HuggingFace dataset support
pip install simple_NER "ahocorasick-ner[datasets]"
```

---

## Wikidata Entities (Easiest)

Use dedicated subclasses: **no QIDs required**.

### Available Subclasses

| Class | Entity Type | Size | Example |
|-------|-------------|------|---------|
| `WikidataAnimalNER` | `Animal` | 1M+ | dogs, cats, eagles |
| `WikidataPlantNER` | `Plant` | 500k+ | roses, oak trees, wheat |
| `WikidataCountryNER` | `Country` | 195 | USA, Japan, Germany |
| `WikidataCityNER` | `City` | 1M+ | Paris, Tokyo, Berlin |
| `WikidataPersonNER` | `Person` | 100M+ | John, Maria, James |
| `WikidataProfessionNER` | `Profession` | 5k+ | doctor, engineer, teacher |
| `WikidataDiseaseNER` | `Disease` | 10k+ | arthritis, diabetes, flu |
| `WikidataLanguageNER` | `Language` | 7k+ | English, Spanish, Chinese |
| `WikidataSportNER` | `Sport` | 2k+ | football, tennis, skiing |
| `WikidataBodyPartNER` | `BodyPart` | 500+ | heart, lung, arm |
| `WikidataFamilyRelationNER` | `FamilyRelation` | 20+ | mother, father, brother |

### Usage

```python
from ahocorasick_ner.datasets import (
    WikidataAnimalNER,
    WikidataCountryNER,
    WikidataProfessionNER,
    WikidataDiseaseNER,
)
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()

# Add multiple entity types
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAnimalNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataCountryNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataProfessionNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataDiseaseNER()))

# Extract
text = "Dr. Smith, a doctor in Paris, treats patients with arthritis. Dogs are popular in many countries."
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
```

**Output:**
```
Profession       → doctor
Country          → Paris
Disease          → arthritis
Animal           → Dogs
Country          → many countries
```

### Multilingual Support

All Wikidata subclasses are multilingual:

```python
# German labels
animals_de = WikidataAnimalNER(lang="de-de")

# Spanish labels
professions_es = WikidataProfessionNER(lang="es")

# Japanese labels
diseases_ja = WikidataDiseaseNER(lang="ja")

# Supported: de, es, fr, it, pt, ru, zh, ja, ko, ar, etc.
```

---

## Locations & Names

### GeoNames

280k+ cities and locations worldwide with multilingual names.

```python
from ahocorasick_ner.datasets import GeoNamesNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(GeoNamesNER()))

text = "Paris, Tokyo, and Berlin are major cities"
for entity in pipeline.process(text):
    print(entity.value)
# Paris
# Tokyo
# Berlin
```

**Entity Type Label:** `location`

### Person Names

Person surnames from 30+ countries.

```python
from ahocorasick_ner.datasets import PersonNamesNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(PersonNamesNER()))

text = "John Smith met Maria Garcia in London"
for entity in pipeline.process(text):
    print(entity.value)
# John
# Maria
```

**Entity Type Label:** `person_name`

---

## Entertainment & Media

### IMDB

6.3M+ entertainment industry names.

| Class | Entity Label | Size | Import |
|-------|--------------|------|--------|
| `MovieActorNER` | `movie_actor` | 6.3M | `from ahocorasick_ner.datasets import MovieActorNER` |
| `MovieDirectorNER` | `movie_director` | 128k | `from ahocorasick_ner.datasets import MovieDirectorNER` |
| `MovieComposerNER` | `movie_composer` | 221k | `from ahocorasick_ner.datasets import MovieComposerNER` |

**Example:**
```python
from ahocorasick_ner.datasets import MovieActorNER, MovieDirectorNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(MovieActorNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(MovieDirectorNER()))

text = "A Steven Spielberg film starring Tom Hanks and Meryl Streep"
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
# movie_director      → Steven Spielberg
# movie_actor         → Tom Hanks
# movie_actor         → Meryl Streep
```

### Metal Archives

Metal bands, tracks, and albums from Encyclopedia Metallum.

| Class | Entity Label(s) | Size | Import |
|-------|-----------------|------|--------|
| `MetalArchivesBandsNER` | `metal_band` | 4.6k | `from ahocorasick_ner.datasets import MetalArchivesBandsNER` |
| `MetalArchivesTrackNER` | `metal_band`, `metal_album`, `metal_track` | 205k tracks | `from ahocorasick_ner.datasets import MetalArchivesTrackNER` |

**Example:**
```python
from ahocorasick_ner.datasets import MetalArchivesBandsNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(MetalArchivesBandsNER()))

text = "Black Sabbath and Metallica pioneered heavy metal"
for entity in pipeline.process(text):
    print(entity.value)
# Black Sabbath
# Metallica
```

### Music Genres

Jazz and progressive rock artists.

| Class | Entity Label(s) | Size | Import |
|-------|-----------------|------|--------|
| `JazzNER` | `jazz_artist`, `jazz_genre` | 12.3k | `from ahocorasick_ner.datasets import JazzNER` |
| `ProgRockNER` | `prog_artist`, `prog_genre` | 12.4k | `from ahocorasick_ner.datasets import ProgRockNER` |

---

## Business & E-Commerce

### Company Names

Extract business names from curated company dataset (50k+).

```python
from ahocorasick_ner.datasets import CompanyNamesNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(CompanyNamesNER()))

text = "Apple, Microsoft, and Google are tech leaders"
for entity in pipeline.process(text):
    print(entity.value)
# Apple
# Microsoft
# Google
```

**Entity Type Label:** `company`

---

## Music (Expanded)

### Spotify Tracks

Extract song titles, artist names, and genres from Spotify dataset (200k+ tracks).

```python
from ahocorasick_ner.datasets import SpotifyTracksNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(SpotifyTracksNER()))

text = "Bohemian Rhapsody by Queen is a rock masterpiece"
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
# track_name       → Bohemian Rhapsody
# artist_name      → Queen
# music_genre      → rock
```

**Entity Type Labels:** `track_name`, `artist_name`, `music_genre`

---

## Food & Recipes

### Recipe Ingredients

Extract ingredient names from 2.2M recipes.

```python
from ahocorasick_ner.datasets import RecipeIngredientsNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(RecipeIngredientsNER()))

text = "Combine flour, sugar, butter, and eggs in a bowl"
for entity in pipeline.process(text):
    print(entity.value)
# flour
# sugar
# butter
# eggs
```

**Entity Type Label:** `ingredient`

### Food Products

Extract food product and brand names (4M+ products).

```python
from ahocorasick_ner.datasets import FoodProductsNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(FoodProductsNER()))

text = "I bought Coca-Cola and Lay's chips at the store"
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
# food_product     → Coca-Cola
# brand            → Lay's
```

**Entity Type Labels:** `food_product`, `brand`

---

## Programming & Technology

### Programming Languages

Extract programming language names (50+ languages built-in).

```python
from ahocorasick_ner.datasets import ProgrammingLanguageNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(ProgrammingLanguageNER()))

text = "Python, JavaScript, and Rust are popular languages"
for entity in pipeline.process(text):
    print(entity.value)
# Python
# JavaScript
# Rust
```

**Entity Type Label:** `programming_language`

---

## Extended Wikidata (Advanced)

### Books & Publishing

```python
from ahocorasick_ner.datasets import (
    WikidataAuthorNER,
    WikidataBookNER,
    WikidataPublisherNER,
)
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAuthorNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataBookNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataPublisherNER()))

text = "J.K. Rowling wrote Harry Potter, published by Bloomsbury"
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
```

### Sports

```python
from ahocorasick_ner.datasets import WikidataAthleteNER, WikidataSportsTeamNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAthleteNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataSportsTeamNER()))

text = "Lionel Messi played for Barcelona and Inter Miami"
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
```

### Landmarks & Cultural Sites

```python
from ahocorasick_ner.datasets import (
    WikidataLandmarkNER,
    WikidataUniversityNER,
    WikidataMuseumNER,
)
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataLandmarkNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataUniversityNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataMuseumNER()))

text = "Visit the Eiffel Tower in Paris or the Louvre Museum. Harvard University is nearby."
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
```

### Movies & Entertainment

```python
from ahocorasick_ner.datasets import WikidataMovieNER, WikidataMusicalNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataMovieNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataMusicalNER()))

text = "The Matrix uses synthesizers and electronic instruments"
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
```

---

## Biomedical

### BC5CDR

Diseases and chemicals from biomedical literature.

```python
from ahocorasick_ner.datasets import BC5CDRMedicalNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()

# Diseases
diseases = BC5CDRMedicalNER(entity_type="Disease")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(diseases))

# Chemicals
chemicals = BC5CDRMedicalNER(entity_type="Chemical")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(chemicals))

text = "Aspirin treats headaches and migraines"
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
# Disease         → headaches
# Disease         → migraines
# Chemical        → Aspirin
```

**Entity Type Labels:** `Disease`, `Chemical`

---

## Generic HuggingFace Integration

### For Custom Datasets

Load any HuggingFace dataset with entities in a column.

```python
from ahocorasick_ner.datasets import GenericHFDatasetNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

# Load colors from color-pedia
colors = GenericHFDatasetNER(
    entity_type="Color",
    hf_dataset="boltuix/color-pedia",
    column="name"
)

pipeline = NERPipeline()
pipeline.add_annotator(AhocorasickAnnotatorWrapper(colors))

text = "The red car parked near the blue house"
for entity in pipeline.process(text):
    print(f"{entity.entity_type:15} → {entity.value}")
# Color           → red
# Color           → blue
```

---

## Combining Multiple Datasets

Create a comprehensive entity extractor by combining multiple dataset loaders.

```python
from ahocorasick_ner.datasets import (
    WikidataAnimalNER,
    WikidataCountryNER,
    MovieActorNER,
    GeoNamesNER,
)
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline(dedup_strategy="keep_longest")

# Add multiple datasets
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataAnimalNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(WikidataCountryNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(MovieActorNER()))
pipeline.add_annotator(AhocorasickAnnotatorWrapper(GeoNamesNER()))

text = (
    "Tom Hanks, an actor, visited Paris with his dog. "
    "The trip took them through Japan and other countries."
)

entities_by_type = {}
for entity in pipeline.process(text):
    if entity.entity_type not in entities_by_type:
        entities_by_type[entity.entity_type] = []
    entities_by_type[entity.entity_type].append(entity.value)

for etype, values in sorted(entities_by_type.items()):
    print(f"{etype:15} → {', '.join(values)}")
```

---

## Dataset Filtering (Selective Loading)

Many dataset loaders support filtering by column values to extract only entities matching specific criteria. This reduces automaton size and improves performance.

### Why Filter?

- **Smaller automaton:** 50-90% memory reduction
- **Faster matching:** Fewer entities to check
- **Domain-specific extraction:** Only relevant entities for your use case
- **Production efficiency:** Load only what you need

### Supported Loaders & Filter Parameters

| Loader | Filter Parameters | Examples |
|--------|-------------------|----------|
| `MetalArchivesBandsNER` | `origin`, `genre`, `formed_year_min`, `formed_year_max` | Country, genre, year range |
| `MetalArchivesTrackNER` | `band_origin`, `album_type` | Country, album type (Full-length, EP, Demo, etc.) |
| `SpotifyTracksNER` | `genre`, `popularity_min`, `popularity_max`, `energy_min`, `danceability_min`, `acousticness_min`, `valence_min`, `explicit` | Genre, popularity, audio features |
| `MovieActorNER` | `gender` | Female/Male |
| `RecipeIngredientsNER` | `source` | Gathered or Recipes1M |
| `FoodProductsNER` | `allergen`, `vegan`, `vegetarian`, `organic`, `country` | Dietary restrictions, allergens, origin |
| `GenericHFDatasetNER` | `filter_column`, `filter_value` | Any column, any value |

### Examples

**Metal bands by country, genre, and formation year:**
```python
from ahocorasick_ner.datasets import MetalArchivesBandsNER, MetalArchivesTrackNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()

# Portuguese metal bands
pt_bands = MetalArchivesBandsNER(origin="Portugal")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(pt_bands))

# Swedish black metal bands
se_black = MetalArchivesBandsNER(origin="Sweden", genre="Black Metal")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(se_black))

# Studio albums from 1980-1995
thrash_tracks = MetalArchivesTrackNER(
    album_type="Full-length",
    band_origin="USA"
)
pipeline.add_annotator(AhocorasickAnnotatorWrapper(thrash_tracks))

text = "Moonspell, Bathory, and Metallica formed different eras"
for entity in pipeline.process(text):
    print(f"{entity.value} ({entity.entity_type})")
```

**Spotify tracks by audio features:**
```python
from ahocorasick_ner.datasets import SpotifyTracksNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()

# Popular, danceable rock tracks
dance_rock = SpotifyTracksNER(
    genre="rock",
    popularity_min=70,
    danceability_min=0.7
)
pipeline.add_annotator(AhocorasickAnnotatorWrapper(dance_rock))

# Happy, high-energy upbeat tracks
upbeat = SpotifyTracksNER(
    energy_min=0.8,
    valence_min=0.7
)
pipeline.add_annotator(AhocorasickAnnotatorWrapper(upbeat))

text = "I love Queen songs and upbeat tracks"
for entity in pipeline.process(text):
    print(f"{entity.value}")
```

**Food products by dietary restrictions:**
```python
from ahocorasick_ner.datasets import FoodProductsNER, RecipeIngredientsNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()

# Vegan products
vegan = FoodProductsNER(vegan=True)
pipeline.add_annotator(AhocorasickAnnotatorWrapper(vegan))

# Gluten-free products
gluten_free = FoodProductsNER(allergen="gluten-free")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(gluten_free))

# Organic vegetarian products
organic_veg = FoodProductsNER(organic=True, vegetarian=True)
pipeline.add_annotator(AhocorasickAnnotatorWrapper(organic_veg))

# Recipe ingredients from Gathered source
gathered_ing = RecipeIngredientsNER(source="Gathered")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(gathered_ing))

text = "I need vegan, gluten-free ingredients for baking"
for entity in pipeline.process(text):
    print(f"{entity.value} ({entity.entity_type})")
```

**Movie actors by gender:**
```python
from ahocorasick_ner.datasets import MovieActorNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()

# Female actors (actresses)
actresses = MovieActorNER(gender="Female")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(actresses))

# Male actors
actors = MovieActorNER(gender="Male")
pipeline.add_annotator(AhocorasickAnnotatorWrapper(actors))

text = "Tom Hanks and Meryl Streep starred together"
for entity in pipeline.process(text):
    print(f"{entity.value}")
```

**Generic filtering with any HF dataset:**
```python
from ahocorasick_ner.datasets import GenericHFDatasetNER
from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline

pipeline = NERPipeline()

# Brazilian metal bands
bands = GenericHFDatasetNER(
    entity_type="MetalBand",
    hf_dataset="TigreGotico/metal-archives-bands",
    column="name",
    filter_column="origin",
    filter_value="Brazil"
)
pipeline.add_annotator(AhocorasickAnnotatorWrapper(bands))

text = "Sepultura and Soulfly are from Brazil"
for entity in pipeline.process(text):
    print(f"{entity.value}")
```

---

## Performance Tips

1. **Cache Automatons:** Use the `path` parameter to save/load pre-built automatons:
   ```python
   animals = WikidataAnimalNER(path="/tmp/animals.ahocorasick")
   # First call downloads and saves, subsequent calls load from disk
   ```

2. **Dedup Strategy:** Choose appropriate dedup strategy:
   ```python
   # Keep longer matches when spans overlap
   pipeline = NERPipeline(dedup_strategy="keep_longest")
   ```

3. **Batch Processing:** Use async pipeline for large documents:
   ```python
   from simple_NER.pipeline import AsyncNERPipeline
   
   async_pipeline = AsyncNERPipeline()
   results = await async_pipeline.process_batch_async(texts, max_concurrency=10)
   ```

---

## Complete Dataset Reference

For full details on all available datasets, entity labels, and sizes, see:
- [ahocorasick-ner DATASET_REFERENCE.md](../../Machine\ Learning\ Workspace/ahocorasick-ner/docs/DATASET_REFERENCE.md)

---

## See Also

- [FAQ.md](FAQ.md): Quick reference for common questions
- [examples/wikidata_subclasses_example.py](../examples/wikidata_subclasses_example.py): Runnable examples
- [examples/huggingface_datasets_example.py](../examples/huggingface_datasets_example.py): More examples

---
[← Migration](MIGRATION.md) · [Home](README.md)
