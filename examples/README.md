# Examples

Runnable scripts covering all major simple_NER features.
Each script is self-contained — install `simple_NER` then run directly.

```bash
pip install simple_NER
python examples/<script>.py
```

| Script | Description | Run |
|:---|:---|:---|
| `01_quick_start.py` | `create_pipeline` with email, phone, url, currency, temporal | `python examples/01_quick_start.py` |
| `02_all_annotators.py` | Every annotator on a tailored sentence; shows `data` fields | `python examples/02_all_annotators.py` |
| `03_pipeline_dedup.py` | All four dedup strategies on overlapping spans | `python examples/03_pipeline_dedup.py` |
| `04_custom_keywords.py` | `SimpleNER` with product names; `is_match`, `in_place_annotation`, `entity_lookup` | `python examples/04_custom_keywords.py` |
| `05_location_extraction.py` | `LocationNER` with `label_confidence`; extract from news text | `python examples/05_location_extraction.py` |
| `06_temporal_extraction.py` | `TemporalNER` with `anchor_date`; dates, times, durations | `python examples/06_temporal_extraction.py` |
| `07_currency_multilang.py` | `CurrencyAnnotator` on EN / DE / FR text; EU decimal format | `python examples/07_currency_multilang.py` |
| `08_async_batch.py` | `AsyncNERPipeline.process_batch_async` on 10 sentences concurrently | `python examples/08_async_batch.py` |
| `09_custom_annotator.py` | Subclass `BaseAnnotator`; write a locale `.rx` file; detect ISBNs | `python examples/09_custom_annotator.py` |
| `10_ovos_plugin.py` | `SimpleNERIntentTransformer` config and `match_data` data flow | `python examples/10_ovos_plugin.py` |
| `11_lookup_wordlist.py` | `LookUpNER` with runtime `add_wordlist` / `remove_wordlist` | `python examples/11_lookup_wordlist.py` |
| `12_locale_system.py` | `load_rx`, `load_intents`, `load_wordlist`, `intent_to_regex` directly | `python examples/12_locale_system.py` |
