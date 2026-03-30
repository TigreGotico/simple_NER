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
