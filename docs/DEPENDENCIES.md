# Dependencies

simple_NER is designed to be lightweight with minimal dependencies.

## Core Dependencies

**4 required packages**:

```python
dependencies = [
    "simplematch",              # Pattern matching (Padaos-like)
    "quebra_frases>=0.3.7",     # Text tokenization and span finding
    "ovos-date-parser",         # Datetime extraction
    "ovos-number-parser",       # Written number extraction
]
```

All core dependencies are installed automatically. No optional backends needed!

## Development

```bash
pip install simple_NER[dev]
```

Installs:
- `pytest>=7.0` - Testing
- `pytest-cov>=4.0` - Coverage
- `ruff>=0.1.0` - Linting
- `mypy>=1.0` - Type checking
- `pre-commit>=3.0` - Git hooks

## Dependency Tree

```
simple_NER
├── simplematch (core)
├── quebra_frases (core)
├── ovos-date-parser (core) → temporal_ner
└── ovos-number-parser (core) → numbers_ner
│
└── [dev] pytest, ruff, mypy, pre-commit
```

## Installation

```bash
# Full install (4 deps)
pip install simple_NER

# Development (9 deps)
pip install simple_NER[dev]
```

## Size Comparison

| Installation | Packages | Install Size |
|-------------|----------|--------------|
| **simple_NER** | 4 | ~2 MB |
| simple_NER + dev | 9 | ~15 MB |
| spaCy | 10+ | ~50 MB |
| NLTK + models | 5+ | ~100 MB |

---
[← Tutorials](TUTORIALS.md) · [Home](README.md) · [Installation →](INSTALLATION.md)
