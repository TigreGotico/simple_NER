# SUGGESTIONS.md — simple_NER

Agent proposals for future improvements. Evidence-based; all items include a rationale.

---

## High Priority

### [DONE] S-001 — `NamesNER`: reduce sentence-boundary false positives
- **Status**: Completed 2026-04-01 — sentence-position heuristic added: single words at sentence start (position 0 or after `.!?`) score 0.55 (below default threshold); mid-sentence words score 0.80; multi-word compound names always score 0.85 regardless of position. `sentence_initial` flag added to entity data. 10 new tests in `test/unittests/test_names_ner.py`.
- **File**: `simple_NER/annotators/names_ner.py`

### [DONE] S-002 — `cities.json` deduplication / disambiguation
- **Status**: Completed 2026-03-31 — longest-match-wins dedup added to `LocationNER`; shorter substrings suppressed when longer match covers the same span.
- **File**: `simple_NER/annotators/locations_ner.py`

### [DONE] S-003 — `PhoneAnnotator`: improve international format coverage
- **Status**: Completed 2026-03-31 — locale/en-us/phone.rx wired to `PhoneAnnotator`; space-separated international formats (`+44 20 7946 0958`) now matched via locale patterns.
- **File**: `simple_NER/annotators/phone_ner.py`

---

## Medium Priority

### [DONE] S-004 — `TemporalNER`: use `_temporal_kw` for duration guard too
- **Status**: Completed 2026-03-31 — temporal-keyword guard now applied to duration extraction in `_extract_duration_entities`.
- **File**: `simple_NER/annotators/temporal_ner.py`

### [DONE] S-005 — `LookUpNER` / `LocationNER`: per-label confidence scores
- **Status**: Completed 2026-03-31 — `label_confidence: dict` param added to both `LookUpNER` and `LocationNER`; per-label overrides applied at annotation time.
- **Files**: `lookup_ner.py`, `locations_ner.py`

### [DONE] S-006 — `NERPipeline`: expose span-overlap dedup across annotator types
- **Status**: Completed 2026-03-31 — cross-annotator span-overlap dedup (longest-span-wins) added to `NERPipeline._deduplicate`.
- **File**: `simple_NER/pipeline.py`

### [DONE] S-007 — `opm.py`: accept list of entity types to inject per utterance context
- **Status**: Completed 2026-03-31 — `per_skill_annotators` config key exposed in `SimpleNERIntentTransformer`; pipeline filtered per skill at transform time.
- **File**: `simple_NER/opm.py`

---

## Low Priority

### [DONE] S-008 — Add Italian and Portuguese `temporal_keywords.txt`
- **Status**: Completed 2026-03-31 — `locale/it-it/` and `locale/pt-pt/` date_months.txt added; TemporalNER locale-aware for IT/PT.
- **File**: `simple_NER/res/it-it/`, `simple_NER/res/pt-pt/`

### [DONE] S-009 — `EmailAnnotator`: add local-part length validation (RFC 5321 max 64 chars)
- **Status**: Completed 2026-03-31 — RFC 5321 local-part ≤64 char validation added to `EmailAnnotator.annotate`.
- **File**: `simple_NER/annotators/email_ner.py`

### [DONE] S-010 — `CurrencyAnnotator`: extend `_AMT` to handle European decimal notation (`1.000,50`)
- **Status**: Completed 2026-03-31 — `_AMT` pattern extended and `_normalize_amount()` added; `1.000,50 €` now parses correctly as 1000.50.
- **File**: `simple_NER/annotators/currency_ner.py`

---

## Pending Fixes

### S-011 — Fix `test_no_private_alias_in_source` false-pass bug (TECH-012)
- **Rationale**: Current implementation uses `subprocess.run([sys.executable, "-m", "grep", ...])` which silently fails (Python has no grep module). Test always passes vacuously, providing zero regression protection against the private alias being re-introduced.
- **Approach**: Use pure-Python pathlib walk + regex, or call system `grep` binary directly.
- **Effort**: Low — ~15 lines of code

### S-012 — Document `LookUpNER.add_word()` O(n²) caveat (TECH-013)
- **Rationale**: Users adding many words in a loop will trigger redundant automaton rebuilds. Should be called out in docstring.
- **Approach**: Add note in docstring: "For bulk additions, prefer `add_wordlist()` (single rebuild) over `add_word()` in a loop."
- **Effort**: Trivial — docstring update only

### S-013 — Align type annotations for `_ac` across `LookUpNER` and `LocationNER` (TECH-014)
- **Rationale**: Consistency — both should use `AhocorasickNER | None` type annotation instead of `Any`.
- **File**: `simple_NER/annotators/locations_ner.py:113`
- **Effort**: Trivial — one-line change

### S-014 — Update `AhocorasickAnnotatorWrapper` docstring dataset class examples (TECH-016)
- **Rationale**: Referenced class names (`WikidataEntityNER`, etc.) do not exist in `ahocorasick_ner.datasets`; actual classes are `EncyclopediaMetallvmNER`, `MusicNER`, `ImdbNER`. Documentation should match reality.
- **File**: `simple_NER/annotators/ahocorasick_wrapper.py:59`
- **Effort**: Low — verify installed classes, update docstring
