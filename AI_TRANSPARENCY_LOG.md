# AI_TRANSPARENCY_LOG.md — simple_NER

Date-stamped log of AI-assisted changes.

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
