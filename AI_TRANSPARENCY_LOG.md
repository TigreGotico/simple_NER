# AI_TRANSPARENCY_LOG.md — simple_NER

Date-stamped log of AI-assisted changes.

---

## 2026-04-01 (sprint 2)

**AI Model**: Claude Sonnet 4.6

**Actions Taken**:
- `refactor`: Removed `_AhocorasickNER` private alias from `lookup_ner.py` and `locations_ner.py`; import is now under public name `AhocorasickNER`. Type annotation string literal on `_ac` field also cleaned up.
- `feat`: Added `min_word_len: int = 5` keyword-only param to `AhocorasickAnnotatorWrapper.__init__`; forwarded to `AhocorasickNER.tag()` on every `annotate()` call.
- `feat`: Added `LookUpNER.add_word(label, word)` for single-word runtime registration (previously only `add_wordlist()` existed).
- `docs`: Rewrote `AhocorasickAnnotatorWrapper` class docstring with two usage examples (custom vocab + dataset loader). Added `AhocorasickAnnotatorWrapper` section to `docs/index.md` with constructor param table.
- `test`: +6 tests — `min_word_len` forwarding (default + custom), `LookUpNER.add_word` (new label, existing label, rebuild), no-private-alias source check. Total: 468 tests.

**Oversight**: Human reviewed and approved all commits before push.

---

## 2026-04-01

**AI Model**: Claude Sonnet 4.6

**Actions Taken**:
- `feat`: Added `AhocorasickAnnotatorWrapper` (`simple_NER/annotators/ahocorasick_wrapper.py`) — adapts any `ahocorasick-ner` dataset loader as a `BaseAnnotator` for use in `NERPipeline`
- `feat`: Added 3 example scripts (`examples/huggingface_datasets_example.py`, `examples/wikidata_subclasses_example.py`, `examples/comprehensive_datasets_example.py`)
- `feat`: Added `docs/DATASET_INTEGRATION.md` — full HuggingFace dataset integration guide
- `test`: Added `test/unittests/test_ahocorasick_wrapper.py` and `test_integration_hf.py` (10 tests)
- `fix`: `NamesNER` sentence-boundary heuristic (S-001) — sentence-initial single words score 0.55 (suppressed); mid-sentence 0.80; compound names 0.85
- `test`: Added `test/unittests/test_names_ner.py` (10 tests)
- `fix`: `utils/diff.py` — replaced `typing.Tuple` with built-in `tuple` (closes TECH-004)
- `test`: Added `test/unittests/test_diff.py`, `test_batch.py`, `test_cli.py` (34 tests)
- Coverage raised from 79% to 89%

**Oversight**: Human reviewed and approved all commits before push.
