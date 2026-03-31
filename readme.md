# simple_NER

Lightweight named-entity recognition library with pluggable annotators, multi-language support, and an async pipeline.

[![PyPI - Version](https://img.shields.io/pypi/v/simple_NER.svg)](https://pypi.org/project/simple_NER/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/simple_NER.svg)](https://pypi.org/project/simple_NER/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/OpenJarbas/simple_NER/build_tests.yml)](https://github.com/OpenJarbas/simple_NER/actions)

## Installation

```bash
pip install simple_NER
pip install "simple_NER[dev]"   # + testing tools
```

## Quick Start

```python
from simple_NER import create_pipeline

pipe = create_pipeline(["email", "phone", "url", "temporal", "currency"])
for entity in pipe.process("Call +1-800-555-0100 or email info@example.com by 2025-06-01"):
    print(entity.entity_type, entity.value, entity.confidence)
# phone    +1-800-555-0100   0.9
# email    info@example.com  1.0
# date     2025-06-01        0.85
```

## Annotators

| Factory key(s) | Class | Detects | Language |
|:---|:---|:---|:---|
| `email`, `email_regex` | EmailAnnotator / EmailNER | Email addresses | Any |
| `names` | NamesNER | Person names (noun heuristic, confidence 0.65–0.8) | English / Latin |
| `locations`, `countries`, `cities` | LocationNER | Countries, capitals, cities | All (wordlist) |
| `temporal`, `datetime`, `duration` | TemporalNER | Dates, times, durations | `lang` param |
| `numbers`, `written_numbers` | NumberNER | Numeric and written numbers | `lang` param |
| `lookup`, `wordlist` | LookUpNER | Custom wordlists | `lang` param |
| `url`, `urls` | URLAnnotator | HTTP/HTTPS URLs | Any |
| `phone`, `phone_number` | PhoneAnnotator | Phone numbers | Any |
| `currency`, `money` | CurrencyAnnotator | Amounts + currency symbol/code | Any |
| `organization`, `org`, `company` | OrganizationAnnotator | Org/company names | `lang` param |
| `hashtag`, `hashtags`, `tag` | HashtagAnnotator | #hashtags | Any |
| `date`, `dates` | DateAnnotator | Structured date strings | `lang` param |

### Key annotator parameters

**LocationNER**: `include_countries=True`, `include_capitals=True`, `include_cities=False`,
`label_confidence={"City": 0.7, "Country": 0.95}`

**PhoneAnnotator**: `require_country_code=False`, `min_length=7`

**OrganizationAnnotator**: `strict_mode=False` (when True, requires corporate suffix like Inc./GmbH)

**TemporalNER / NumberNER / DateAnnotator / LookUpNER**: `lang="en-us"`, optionally `anchor_date` for TemporalNER

## Entity Data Fields

Each `Entity` carries a `data` dict with annotator-specific fields:

| Annotator | Extra fields in `data` |
|:---|:---|
| EmailAnnotator | `local_part`, `domain`, `start`, `end` |
| URLAnnotator | `protocol`, `start`, `end` |
| PhoneAnnotator | `digits`, `digit_count`, `type` (international/us_national/local/other), `has_country_code`, `start`, `end` |
| CurrencyAnnotator | `amount` (float), `currency` (ISO code), `currency_symbol`, `start`, `end` |
| LocationNER | `country_code`, `label`, `start`, `end` |
| HashtagAnnotator | `tag_type` (shouting/lowercase/CamelCase/underscored/alphanumeric/mixed), `start`, `end` |
| OrganizationAnnotator | `org_type` (company/educational/medical/other), `start`, `end` |
| NumberNER | `number` (str, digit form), `start`, `end` |
| DateAnnotator | `year`, `month`, `day`, `format`, `start`, `end` |

## Pipeline Dedup Strategies

`NERPipeline` and `AsyncNERPipeline` accept a `dedup_strategy` argument:

| Strategy | Behaviour |
|:---|:---|
| `keep_all` | Return every entity span, including overlaps |
| `keep_longest` | When spans overlap, keep the longer one |
| `keep_higher_confidence` | When spans overlap, keep the higher-confidence one |
| `keep_first` | When spans overlap, keep the first one encountered |

```python
pipe = create_pipeline(["currency", "numbers"], dedup_strategy="keep_longest")
```

## Locale / i18n System

Annotators load language-specific patterns from `simple_NER/locale/<lang>/`:

| Extension | Content | Loader |
|:---|:---|:---|
| `.rx` | One raw regex per line | `load_rx(name, lang)` |
| `.intent` | NL templates `{var}` → named capture | `load_intents(name, lang)` |
| `.txt` | Plain wordlist, one entry per line | `load_wordlist(name, lang)` |

All loaders fall back to `en-us` when no language-specific file exists.
`intent_to_regex("{amount} dollars")` converts an intent template to a compiled `re.Pattern`.

**Adding a new language**: create `simple_NER/locale/<lang>/` and place `.rx`, `.intent`, or `.txt` files
that override the `en-us` defaults. Only the files you add are used; everything else falls back automatically.
Inside a `BaseAnnotator` subclass, `self._load_rx("name")` and `self._load_intents("name")` resolve
to `self.lang` automatically.

Existing locale data: `en-us` (phone, email, url, hashtag, currency, organization, date_months),
`de-de` (currency, organization, date_months), `es`/`fr`/`it`/`nl`/`pt` (date_months).

## Async Batch Processing

```python
import asyncio
from simple_NER.annotators.async_pipeline import AsyncNERPipeline

pipe = AsyncNERPipeline(dedup_strategy="keep_longest")
pipe.add_annotator(...)

async def run():
    results = await pipe.process_batch_async(sentences, max_concurrency=10)

asyncio.run(run())
```

## OVOS Plugin

simple_NER ships an intent-transformer plugin for the OpenVoiceOS / OVOS ecosystem.
Entry-point group: `opm.transformer.intent`, key: `simple-ner-transformer`, priority 50,
class: `SimpleNERIntentTransformer`.

```json
{
  "intent_transformers": {
    "simple-ner-transformer": {
      "annotators": ["email", "phone", "temporal", "currency"],
      "confidence_threshold": 0.6,
      "lang": "en-us"
    }
  }
}
```

The transformer runs the configured pipeline on every utterance and injects recognized entities
into `match_data` before intent handling proceeds.

## Links

- [docs/index.md](docs/index.md) — full API reference and architecture
- [docs/TUTORIALS.md](docs/TUTORIALS.md) — step-by-step tutorials
- [docs/API.md](docs/API.md) — detailed class and method docs
- [examples/README.md](examples/README.md) — runnable example index
- [GitHub](https://github.com/OpenJarbas/simple_NER)
