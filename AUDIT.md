# AUDIT.md — simple_NER

Evidence-based issues with `file.py:LINE` citations.

---

## Open Issues

### TECH-009 — `CurrencyAnnotator.CURRENCY_PATTERN` character-class bug
- **File**: `simple_NER/annotators/currency_ner.py:91`
- **Severity**: Low
- **Detail**: Multi-char symbols `R$`, `A$`, `C$` are inserted into a regex character class `[...]` which treats each character individually. Result: bare `R`, `A`, `C` match single letters (e.g. `a 30` matches because `A` ≡ `a` under `re.IGNORECASE`). Fix: handle multi-char symbols separately before the character-class branch.

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
