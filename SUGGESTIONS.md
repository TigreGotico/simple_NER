# SUGGESTIONS.md — simple_NER

Agent proposals for future improvements. Evidence-based; all items include a rationale.

---

## High Priority

### S-001 — `NamesNER`: replace regex with a lightweight NER model
- **Rationale**: The current capitalised-word regex produces ~30% false positives even with stopword filtering (e.g. "Send", "Meeting" at sentence boundaries). A small spaCy `en_core_web_sm` or `spacy-lookups-data` model would cut false positives dramatically with minimal overhead.
- **Alternative**: Use `LookUpNER` with a first-name/last-name wordlist (e.g. from `names-dataset`) as a complement to the regex pass.
- **File**: `simple_NER/annotators/names_ner.py`

### S-002 — `cities.json` deduplication / disambiguation
- **Rationale**: "York" (England) shadows "New York" because both appear in the city list and Aho-Corasick finds the shorter match first. Sorting patterns longest-first at automaton build time, or filtering single-word cities below a population threshold, would reduce noise.
- **File**: `simple_NER/annotators/locations_ner.py:_build_automaton`

### S-003 — `PhoneAnnotator`: improve international format coverage
- **Rationale**: Space-separated international formats (`+44 20 7946 0958`, `+33 1 23 45 67 89`) partially match only the trailing digits. The pattern needs a separate branch for `\+\d{1,3}(?:[\s-]\d{2,4}){2,4}`.
- **File**: `simple_NER/annotators/phone_ner.py`

---

## Medium Priority

### S-004 — `TemporalNER`: use `_temporal_kw` for duration guard too
- **Rationale**: The keyword guard is only applied to datetime spans; duration spans could also produce false positives from bare numbers (e.g. "$500" → "500 seconds").
- **File**: `simple_NER/annotators/temporal_ner.py:_extract_duration_entities`

### S-005 — `LookUpNER` / `LocationNER`: per-label confidence scores
- **Rationale**: Country matches are high-confidence; city single-word matches are lower. Let callers configure `{"City": 0.7, "Country": 0.95}` at init time.
- **Files**: `lookup_ner.py`, `locations_ner.py`

### S-006 — `NERPipeline`: expose span-overlap dedup across annotator types
- **Rationale**: Money and written_number often overlap on the same span (e.g. `$500`). The dedup only groups exact-span duplicates; overlapping spans from different annotators are both yielded. A longest-span wins strategy across types would clean this up.
- **File**: `simple_NER/pipeline.py:_deduplicate`

### S-007 — `opm.py`: accept list of entity types to inject per utterance context
- **Rationale**: Some OVOS skills only want `date_time` or `number`; running the full pipeline for every utterance is wasteful. Expose a `per_skill_annotators` config key.
- **File**: `simple_NER/opm.py`

---

## Low Priority

### S-008 — Add Italian and Portuguese `temporal_keywords.txt`
- **Rationale**: `DateAnnotator` already supports IT/PT month names; `TemporalNER` should too.
- **File**: `simple_NER/res/it-it/`, `simple_NER/res/pt-pt/`

### S-009 — `EmailAnnotator`: add local-part length validation (RFC 5321 max 64 chars)
- **File**: `simple_NER/annotators/email_ner.py`

### S-010 — `CurrencyAnnotator`: extend `_AMT` to handle European decimal notation (`1.000,50`)
- **Rationale**: The current pattern treats `.` as decimal separator only. In DE/ES/FR/IT the comma is the decimal separator and dot is the thousands separator.
- **File**: `simple_NER/annotators/currency_ner.py`
