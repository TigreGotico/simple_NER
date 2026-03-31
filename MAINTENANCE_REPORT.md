# Maintenance Report — simple_NER

## 2026-03-30 — Phase 1 Revival

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-reviewed plan; AI executed all code changes

### Actions Taken

1. **pyproject.toml** — Fixed broken `build-backend` (`setuptools.backends.legacy:build` → `setuptools.build_meta`); added `setuptools-scm` to `build-system.requires`. All extras (`datetime`, `units`, `keywords`, `nltk`, `remote`) already present. `python_requires = ">=3.10"` confirmed.

2. **simple_NER/__init__.py** — Replaced `types.new_class()` dynamic subclass creation with `_SimpleNamespace` (plain attribute container). Added full type hints and docstrings to `Entity`, `SimpleNER`, and `find_all`. No behavioural changes for flat `data` keys; nested dicts now yield `_SimpleNamespace` instances instead of anonymous `Entity` subclasses.

3. **simple_NER/rules/__init__.py** — Added type hints and docstrings to `Rule` and `RuleNER`.

4. **simple_NER/rules/rx.py** — Added type hints, docstrings, and null-guard in `_create_regex` (returns `None` on `re.error`; callers skip gracefully).

5. **simple_NER/annotators/__init__.py** — Added type hints and docstrings to `NERWrapper`.

6. **test/test_core.py** — 35 unit tests covering `Entity`, `Rule`, `SimpleNER`, `RuleNER`, `RegexNER`, `NERWrapper`. All pass with zero external deps beyond `simplematch` and `quebra_frases`.

7. **docs/index.md** — Created with architecture overview, annotator table, install instructions, quick start, and key-class source citations.

### Test results

```
35 passed in 0.11s
```

---

## 2026-03-30 — opm.py rewrite + NeuralNER removal + docs

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **simple_NER/opm.py** — Complete rewrite. Previous implementation was hallucinated: used a non-existent `IntentTransformerPlugin` base class from a non-existent module path, wrong `__init__` and `transform` signatures, wrong entry point group, and an invalid TOML key. Rewritten as `SimpleNERIntentTransformer(IntentTransformer)` from `ovos_plugin_manager.templates.transformers` following the ahocorasick-ner reference implementation. Entry point changed to `opm.transformer.intent`.

2. **pyproject.toml** — Entry point updated from `ovos.plugin.transformer / simple-ner.transformer` to `opm.transformer.intent / simple-ner-transformer`.

3. **simple_NER/rules/neural.py** — **Deleted.** NeuralNER and padatious dependency removed entirely.

4. **examples/neural.py** — **Deleted** (depended on NeuralNER).

5. **simple_NER/utils/diff.py** — Added type hints and docstrings to `TextDiff.__init__` and `dif_tags`.

6. **AUDIT.md** — Created with 8 tracked issues (TECH-001 through TECH-008).

7. **docs/index.md** — Updated: NeuralNER removed, OVOS plugin section added, annotator table corrected (16 entries).

8. **readme.md** — Fixed annotator count (22→16), removed NeuralNER/padatious references, added OVOS Integration section.

9. **test/test_opm.py** — Rewritten to test the real `IntentHandlerMatch`-based API (10 tests).

### Test results

```
10 passed in 5.60s (test_opm.py)
```

---

## 2026-03-31 — Improved language support across all annotators

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **TemporalNER** (`temporal_ner.py`) — Added `lang: str = "en-us"` param; forwarded to all `ovos-date-parser` and `ovos-number-parser` calls (`extract_datetime`, `extract_duration`, `nice_date`, `nice_duration`, `convert_words_to_numbers`). Now truly multi-language.

2. **NumberNER** (`numbers_ner.py`) — Added `lang: str = "en-us"` param; forwarded to `convert_words_to_numbers`. Factory kwargs (`create_pipeline(["numbers"], lang="de-de")`) now work end-to-end.

3. **DateAnnotator** (`date_ner.py`) — Added month names for Spanish, French, German, Portuguese, Italian, and Dutch. Pattern now built dynamically from the `MONTHS` dict at `__init__` time (longest token first) so any future additions are automatic.

4. **CurrencyAnnotator** (`currency_ner.py`) — Added `WRITTEN_WORDS` dict with currency words in 7 languages (en/es/fr/de/pt/it/nl). Added fourth branch to `CURRENCY_PATTERN` matching `<amount> <word>`. Updated `_parse_currency` to resolve written words to ISO codes.

5. **OrganizationAnnotator** (`organization_ner.py`) — Replaced English-only suffix list with `_COMPANY_SUFFIXES` covering GmbH, AG, KG, UG, SA, SAS, SARL, EURL, SRL, SpA, Ltda, BV, NV, SE, SCE. Name pattern extended to match accented Latin characters (`\u00C0-\u024F`). Added multilingual edu/medical keywords. Updated `_classify_org`.

### Test results

```
183 passed, 3 skipped
```

---

## 2026-03-30 — AUDIT cleanup + language support

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **simple_NER/annotators/temporal_ner.py** — Removed lingua_nostra fallback entirely. Simplified import block to ovos-date-parser only. Removed redundant warning from `annotate()` (module-level warning on import failure is sufficient). Updated docstring.

2. **simple_NER/annotators/numbers_ner.py** — Same: removed lingua_nostra fallback, simplified import block, cleaned up `__main__` block.

3. **All 11 annotator classes** — Added ``Language support:`` line to every class docstring (email, names, locations, temporal, numbers, url, phone, currency, organization, hashtag, date).

4. **simple_NER/benchmark.py** → **examples/benchmark.py** — Moved from package to examples; it is a standalone CLI tool, not part of the importable library.

5. **AUDIT.md** — Closed TECH-002, TECH-005, TECH-008; no open issues remain.

---

## 2026-03-30 — Cleanup pass (AUDIT items)

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **setup.py** — Deleted. Superseded by `pyproject.toml`. Had stale deps (nltk, quantulum3, lingua_nostra, RAKEkeywords, fann2, requests) that no longer apply.

2. **simple_NER/keywords/** — Deleted entire directory (`rake.py` was a 26-byte stub; `__init__.py` was empty). Nothing in the codebase referenced it.

3. **pyproject.toml** — Bumped version 0.8.1 → 0.9.0 to match `cli.py`.

4. **docs/FAQ.md** — Rewrote: removed padatious/NeuralNER references, removed quantulum3/lingua_nostra install instructions, added OVOS plugin configuration Q&A, added language support Q&A, reduced to necessary content only.

5. **AUDIT.md** — Closed TECH-001, TECH-003, TECH-004, TECH-006, TECH-007; added setup.py entry; reduced to 3 open issues.


---

## 2026-03-31 — Unicode hashtags, session lang in OPM, BaseAnnotator lang param

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **simple_NER/annotators/hashtag_ner.py** — Replaced `[A-Za-z0-9_]` character class with `\w` (Unicode) and added `re.UNICODE` flag. `HashtagAnnotator` now matches hashtags in any script: Arabic `#هاشتاق`, Japanese `#タグ`, Chinese `#标签`, Cyrillic `#тег`. Updated docstring.

2. **simple_NER/annotators/base.py** — Added `lang: str = "en-us"` to `BaseAnnotator.__init__`. All annotators now carry a `.lang` attribute without needing to declare it independently. Subclasses that already accept `lang` (e.g. `TemporalNER`, `NumberNER`) now forward it via `super().__init__(confidence=confidence, lang=lang)` instead of setting `self.lang` manually.

3. **simple_NER/annotators/temporal_ner.py** — Removed redundant `self.lang = lang`; delegated to `super().__init__(confidence=confidence, lang=lang)`.

4. **simple_NER/annotators/numbers_ner.py** — Same: removed redundant `self.lang = lang`; delegated to `super()`.

5. **simple_NER/opm.py** — Session-language awareness added to `SimpleNERIntentTransformer`:
   - Added `_default_lang` config key (`"lang"`, default `"en-us"`).
   - `pipeline` property replaced by `_get_pipeline(lang)` which rebuilds only when language changes.
   - `transform()` resolves `lang` from `intent.updated_session.lang` → `SessionManager.get()` → config default (in that priority order).
   - Added optional `SessionManager` import (no-op if unavailable).

6. **AUDIT.md** — Added TECH-009: pre-existing `CurrencyAnnotator` character-class bug where multi-char symbols `R$`, `A$`, `C$` are split by the regex engine.

7. **docs/FAQ.md** — Expanded language support answer to a full table covering all annotators.

8. **test/test_opm.py** — Updated `TestPipelineLazyInit` to use `_get_pipeline()` instead of `pipeline`; added `test_pipeline_rebuilds_on_lang_change`.

9. **test/test_new_annotators.py** — Added 20 multilingual/Unicode tests covering: Arabic/Japanese/Chinese/Cyrillic hashtags, Spanish/French/German/Italian/Portuguese date months, written currency words, international org suffixes, and `lang` attribute propagation.

### Test results

```
203 passed, 3 skipped
```

---

## 2026-03-31 — API compatibility fixes + CurrencyAnnotator bug fix

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **simple_NER/annotators/numbers_ner.py** — Added compatibility shim for `ovos-number-parser` API change: `convert_words_to_numbers` → `numbers_to_digits(utterance, lang, scale)`. Auto-detected at import time via `inspect.signature`. `short_scale` mapped to `Scale.SHORT/LONG` enum.

2. **simple_NER/annotators/temporal_ner.py** — Same `_convert_numbers` shim applied. All `ovos_date_parser` calls updated to new positional `lang` API:
   - `extract_datetime(text, lang, anchorDate)` (was `extract_datetime(text, anchorDate, lang=lang)`)
   - `extract_duration(text, lang)` (was `extract_duration(text, lang=lang)`)
   - `nice_date(dt, lang, now=anchor)` (was `nice_date(dt, now=anchor, lang=lang)`)
   - `nice_duration(total_seconds, lang)` (was `nice_duration(timedelta, lang=lang)`)

3. **simple_NER/annotators/currency_ner.py** — Fixed TECH-009:
   - `CURRENCY_PATTERN` now built by `_build_pattern()` classmethod instead of inline.
   - Multi-char symbols `R$`, `A$`, `C$` handled via regex alternation, not character class — eliminating false matches on bare `R`/`A`/`C` letters.
   - `_parse_currency()` symbol loop now sorts longest-first so `A$` beats `$`.

4. **AUDIT.md** — Closed TECH-009 and added TECH-010 (now also closed).

### Test results

```
206 passed (was 203 passed + 3 skipped)
```

The 3 previously skipped `TestTemporalNER` tests now pass — `ovos-date-parser` and `ovos-number-parser` were installed and the API compatibility shims were added.

---

## 2026-03-31 — IDN URLs, NamesNER stopword filter, URL Unicode

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **simple_NER/annotators/url_ner.py** — Added IDN (internationalized domain name) support. `URL_PATTERN` now uses `_LABEL_CHAR` covering Latin Extended-A/B (`\u00C0-\u024F`), Cyrillic (`\u0400-\u04FF`), CJK (`\u4E00-\u9FFF`), Hiragana, Katakana. Added `re.UNICODE` flag. `https://münchen.de` now detected.

2. **simple_NER/annotators/names_ner.py** — Added `_STOPWORDS` frozenset (~50 entries) filtering high-frequency false positives: sentence-opening words (The, A, In, On…), pronouns, weekdays, months, and common English nouns that appear capitalised. Checked before yielding each entity.

### Test results

```
206 passed
```

---

## 2026-03-31 — stopwords-iso integration for NamesNER

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **simple_NER/annotators/names_ner.py** — Replaced ~50-entry hardcoded `_STOPWORDS` set with `_load_stopwords_iso("en")` module-level function that reads `stopwordsiso/stopwords-iso.json` directly via `importlib.util.find_spec` + pathlib (bypassing the broken `pkg_resources` import in `stopwordsiso.__init__` on Python 3.13). Returns 2590 entries (lowercase + Title-case). Falls back to minimal hardcoded set if package absent.

2. **pyproject.toml** — `stopwordsiso>=0.6.1` and `setuptools>=82.0.1` already present as core dependencies.

### Test results

```
206 passed
```

---

## 2026-03-31 — TemporalNER false-positive filter, LookUpNER Aho-Corasick, NumberNER numeric guard

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **simple_NER/annotators/temporal_ner.py** — Added `_ORDINAL_RE` and `_load_temporal_keywords(lang)` at module level. Temporal keyword list now loaded from `res/<lang>/temporal_keywords.txt` (falls back to `en-us`). False-positive guard: diff spans that contain no temporal keyword and no ordinal (e.g. "the 500" from currency normalisation) are skipped. Added `import re` and `import pathlib`.

2. **simple_NER/res/en-us/temporal_keywords.txt** — Created (42 English keywords).

3. **simple_NER/res/{de-de,es-es,fr-fr}/temporal_keywords.txt** — Created for German, Spanish, French.

4. **simple_NER/annotators/numbers_ner.py** — Added numeric guard: only yield `written_number` entities where the replacement string is a pure number (digits, `.`, `,`, `±`). Eliminates spurious matches from email addresses and phone numbers that `numbers_to_digits` reformats as a side-effect.

5. **simple_NER/annotators/lookup_ner.py** — Added `ahocorasick-ner` backend:
   - Optional import of `AhocorasickNER`; graceful regex fallback if absent.
   - `_build_automaton()` builds automaton after `_load_entities()`, `add_wordlist()`, `remove_wordlist()`.
   - `annotate()` uses `ac.tag()` (O(N) single-pass) when automaton is available.
   - Entity data now includes `start`/`end` positions from AC matches.

6. **pyproject.toml** — Added `ahocorasick-ner>=0.1.1` to core dependencies.

### Test results

```
206 passed
```

---

## 2026-03-31 — LocationNER Aho-Corasick, hard deps, phone extensions, __all__

**AI Model**: claude-sonnet-4-6
**Oversight**: Human-directed; AI executed all changes

### Actions Taken

1. **simple_NER/annotators/locations_ner.py** — Replaced O(N_words × N_locations) word-loop with Aho-Corasick automaton (`_build_automaton`). Multi-word names like "New York", "Los Angeles", "United States" now detected correctly. Legacy word-scan removed entirely. `ahocorasick-ner` is now a hard dependency (no try/except).

2. **simple_NER/annotators/lookup_ner.py** — Removed try/except import and regex fallback. `ahocorasick-ner` hard dependency. `annotate()` simplified to pure AC path.

3. **simple_NER/annotators/phone_ner.py** — Added `_EXT` suffix pattern `(?:\s*(?:x|ext\.?)\s*\d{1,5})?`. Numbers like `+1-555-867-5309 x123` and `(555) 123-4567 ext. 456` now captured in full.

4. **simple_NER/__init__.py** — Added `__all__ = ["Entity", "SimpleNER"]`.

5. **SUGGESTIONS.md** — Created with 10 tracked improvement proposals (S-001 through S-010).

### Test results

```
206 passed
```
