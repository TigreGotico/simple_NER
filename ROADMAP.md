# simple_NER — Revival Roadmap

## Why revive

Modular multi-backend NER with a clean annotator architecture: rule-based (simplematch/regex), neural (padatious), and 10+ domain-specific annotators (dates, emails, locations, units, keywords). Each annotator is independently useful. Entity results carry confidence, source, span, and metadata — richer than most lightweight NER libraries. Good complement to `ahocorasick-ner` for cases where rule-based extraction beats neural.

**Note:** Before reviving, audit overlap with `ahocorasick-ner` in the ML Workspace. If all annotators are already covered there, archive this instead.

---

## Phase 1 — Audit & Stabilize (week 1)

**Goal:** Determine what's worth keeping; make it installable.

- [ ] **Gap analysis vs `ahocorasick-ner`**: list every `simple_NER` annotator and check if it exists in ahocorasick-ner. Only proceed with annotators not covered there.
- [ ] Replace `setup.py` with `pyproject.toml`; add `python_requires = ">=3.10"`
- [ ] Audit `types.new_class()` dynamic class creation in `__init__.py` — replace with explicit `@property` definitions on `Entity`
- [ ] Split into core + optional extras:
  - Core: `RuleNER`, `RegexNER`, `Entity` (no external deps beyond `simplematch`)
  - `[datetime]`: `DateTimeNER`, `TimedeltaNER` (lingua_nostra)
  - `[units]`: `UnitsNER` (quantulum3)
  - `[keywords]`: `KeywordNER` (RAKEkeywords)
  - `[nltk]`: `NltkNER`
  - `[remote]`: `SpotlightNER`, `SnipsNER`
- [ ] Audit `lingua_nostra`, `RAKEkeywords`, `quebra_frases` maintenance status — replace or vendor if unmaintained
- [ ] Write unit tests for `RuleNER` and `RegexNER` (core, zero external deps)

---

## Phase 2 — Modernize (week 2)

**Goal:** Typed, clean, maintainable annotator API.

- [ ] Add type hints to `Entity`, `SimpleNER`, `RuleNER`, `RegexNER`, `NERWrapper`
- [ ] Define `Annotator` protocol/ABC with a single required method: `extract_entities(text: str) -> list[Entity]`
- [ ] Make `NERWrapper` accept any `Annotator` implementation — currently tightly coupled
- [ ] Add docstrings to all public classes
- [ ] Write `docs/index.md` with annotator table and usage examples

---

## Phase 3 — Consolidate (optional, future)

**Goal:** Merge the best annotators into `ahocorasick-ner` and archive this repo.

- [ ] Port any unique annotators not in ahocorasick-ner (likely: `DateTimeNER`, `UnitsNER`, custom rule patterns)
- [ ] Deprecate `simple_NER` in favour of `ahocorasick-ner` with a clear migration note in README
- [ ] Archive repo

---

## Annotator inventory (for gap analysis)

| Annotator | Unique to simple_NER? | Dependency |
|---|---|---|
| `RuleNER` (simplematch) | Possibly | simplematch |
| `RegexNER` | Possibly | stdlib |
| `NeuralNER` (padatious) | Unlikely | padatious |
| `EmailNER` | Check | stdlib |
| `NamesNER` | Check | — |
| `LocationNER` / `CitiesNER` | Check | — |
| `DateTimeNER` / `TimedeltaNER` | Check | lingua_nostra |
| `UnitsNER` | Check | quantulum3 |
| `KeywordNER` (RAKE) | Check | RAKEkeywords |
| `NumberNER` | Check | — |
| `NltkNER` | Check | nltk |
| `SpotlightNER` (DBpedia) | Check | requests |
