# AUDIT.md — simple_NER

Evidence-based issues with `file.py:LINE` citations.

---

## Open Issues

### TECH-011 — `NumberNER`: entities missing `start`/`end` span positions
- **Severity**: Medium
- **File**: `simple_NER/annotators/numbers_ner.py`
- **Detail**: `written_number` entities yielded by `NumberNER.annotate()` set `start=0, end=0` (or omit span entirely). Unlike `LookUpNER` and `LocationNER` which use Aho-Corasick and return accurate byte offsets, `NumberNER` uses `numbers_to_digits()` string diffing which does not preserve original span positions. Callers relying on `entity.data["start"]` / `entity.data["end"]` for downstream highlighting or slot-filling will receive incorrect values.
- **Workaround**: Re-scan the original text for the matched number string after extraction.

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
| TECH-004 | `utils/diff.py` untyped | 2026-03-30 |
| TECH-006 | `opm.py` hallucinated OVOS API | 2026-03-30 — rewritten |
| TECH-007 | NeuralNER stale reference | 2026-03-30 — moot (file deleted) |
| setup.py | Stale setup.py with wrong deps | 2026-03-30 — deleted |
| TECH-002 | `benchmark.py` untested/undocumented | 2026-03-30 — moved to examples/ |
| TECH-008 | Language support undocumented | 2026-03-30 — added to all annotator docstrings |
| TECH-009 | `CurrencyAnnotator` char-class bug (R$/A$/C$) | 2026-03-31 — fixed with `_build_pattern()` + longest-first symbol sort |
| TECH-010 | `ovos-number-parser` / `ovos-date-parser` API mismatch | 2026-03-31 — updated to new positional `lang` signatures |
