# AUDIT.md — simple_NER

Evidence-based issues with `file.py:LINE` citations.

---

## Open Issues

### TECH-012 — `test_no_private_alias_in_source` is a false-pass test
- **Severity**: Major
- **Location**: `test/unittests/test_ahocorasick_wrapper.py:161–170`
- **Description**: The test runs `subprocess.run([sys.executable, "-m", "grep", ...])` but Python has no `grep` module. The command exits with code 1 and empty stdout, making the assertion `result.stdout == ""` always true regardless of whether the private alias exists. This provides **zero regression protection**.
- **Fix**: Use a pure-Python implementation: walk `simple_NER/` with `pathlib` + `re.search`, or call the system `grep` binary directly (`["grep", "-r", ...]`).

### TECH-013 — `LookUpNER.add_word()` has O(n²) complexity in loops
- **Severity**: Minor
- **Location**: `simple_NER/annotators/lookup_ner.py:add_word()`
- **Description**: The method rebuilds the full automaton on every call via `_build_automaton()`. For callers adding many words in a tight loop, this is quadratic. No immediate issue (wordlists are typically small), but worth documenting for users adding large batches.
- **Workaround**: Use `add_wordlist()` for bulk additions (single rebuild), not `add_word()` in a loop.

### TECH-014 — `LookUpNER` and `LocationNER` have inconsistent `_ac` type annotations
- **Severity**: Minor
- **Location**: `simple_NER/annotators/lookup_ner.py:67` vs `locations_ner.py:113`
- **Description**: `lookup_ner.py` uses `AhocorasickNER | None` while `locations_ner.py` uses `Any`. After the import rename (from `_AhocorasickNER` to `AhocorasickNER`), the types should be aligned for consistency.
- **Fix**: Align `locations_ner.py:113` to use `AhocorasickNER | None` type annotation.

### TECH-015 — `LookUpNER` docstring references stale fallback behaviour
- **Severity**: Minor
- **Location**: `simple_NER/annotators/lookup_ner.py:25–26`
- **Description**: Class docstring states "Falls back to per-pattern `re.search` if the package is absent" but `ahocorasick-ner` is now a hard dependency in `pyproject.toml`. The fallback sentence is inaccurate.
- **Fix**: Remove the fallback reference or clarify that `ahocorasick-ner` is always present.

### TECH-016 — `AhocorasickAnnotatorWrapper` docstring references non-existent dataset classes
- **Severity**: Minor
- **Location**: `simple_NER/annotators/ahocorasick_wrapper.py:59` (Args block)
- **Description**: Docstring references `WikidataEntityNER`, `GenericHFDatasetNER`, `BC5CDRMedicalNER` as example dataset classes, but the installed `ahocorasick_ner.datasets` module exports different names (`EncyclopediaMetallvmNER`, `MusicNER`, `ImdbNER`). Stale documentation.
- **Fix**: Update docstring examples to reflect actual available dataset classes in the installed version, or remove specific class names and use generic "dataset loader" language.

---

### TECH-008 — Language support documented per-annotator (FIXED 2026-03-30)
- **Severity**: Low → **Fixed**
- **Fix**: Added ``Language support:`` line to every annotator class docstring. lingua_nostra fallback removed from `temporal_ner.py` and `numbers_ner.py`.

---

## Resolved Issues

| ID | Issue | Fixed |
|----|-------|-------|
| TECH-001 | `keywords/rake.py` 26-byte stub | 2026-03-30 — deleted |
| TECH-003 | NeuralNER / padatious removed | 2026-03-30 — deleted |
| TECH-004 | `utils/diff.py` untyped | 2026-04-01 — `Tuple` replaced with built-in `tuple`, unused `typing.Tuple` import removed |
| TECH-006 | `opm.py` hallucinated OVOS API | 2026-03-30 — rewritten |
| TECH-007 | NeuralNER stale reference | 2026-03-30 — moot (file deleted) |
| setup.py | Stale setup.py with wrong deps | 2026-03-30 — deleted |
| TECH-002 | `benchmark.py` untested/undocumented | 2026-03-30 — moved to examples/ |
| TECH-008 | Language support undocumented | 2026-03-30 — added to all annotator docstrings |
| TECH-009 | `CurrencyAnnotator` char-class bug (R$/A$/C$) | 2026-03-31 — fixed with `_build_pattern()` + longest-first symbol sort |
| TECH-010 | `ovos-number-parser` / `ovos-date-parser` API mismatch | 2026-03-31 — updated to new positional `lang` signatures |
| TECH-011 | `NumberNER` entities missing `start`/`end` span positions | 2026-03-31 — fixed via `_find_replacements()` using `difflib.SequenceMatcher` (commit a5bac24) |
