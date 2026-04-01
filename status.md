# Status: Tighten ahocorasick-ner Integration

## Checklist

- [x] Rename `_AhocorasickNER` import in `lookup_ner.py`; update all usages including string type annotation on line 67
- [ ] Rename `_AhocorasickNER` import in `locations_ner.py`; update usage in `_build_automaton`
- [ ] Add `min_word_len: int = 5` (keyword-only) to `AhocorasickAnnotatorWrapper.__init__`; store and forward to `tag()`
- [ ] Add `LookUpNER.add_word(label, word)` method with automaton rebuild
- [ ] Update `AhocorasickAnnotatorWrapper` docstring with `min_word_len` param doc and dataset-loader example
- [ ] Update `docs/index.md` `AhocorasickAnnotatorWrapper` section
- [ ] Add tests: `min_word_len` forwarding (custom + default), `LookUpNER.add_word`, no-`_AhocorasickNER`-symbol check
- [ ] Run `uv run pytest test/ -v --cov=simple_NER --cov-report=term-missing`; confirm 462+ pass, coverage ≥ 89%

## Blockers

<!-- populated by /implement-task if something is stuck -->
