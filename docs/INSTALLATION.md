# Installation Guide

This guide covers all installation options for simple_NER.

## Table of Contents

- [Basic Installation](#basic-installation)
- [Optional Dependencies](#optional-dependencies)
- [Development Setup](#development-setup)
- [Docker Installation](#docker-installation)
- [Troubleshooting](#troubleshooting)

---

## Basic Installation

### From PyPI

```bash
pip install simple_NER
```

### From Source

```bash
git clone https://github.com/OpenJarbas/simple_NER.git
cd simple_NER
pip install -e .
```

### Specific Version

```bash
pip install simple_NER==0.9.0
```

---

## Optional Dependencies

### All Features

Install everything:

```bash
pip install simple_NER[all]
```

### Individual Features

```bash
# Physical units and measurements
pip install simple_NER[units]

# Keyword extraction
pip install simple_NER[keywords]

# NLTK integration
pip install simple_NER[nltk]

# Remote APIs (DBpedia Spotlight, etc.)
pip install simple_NER[remote]
```

### Development Dependencies

```bash
pip install simple_NER[dev]
```

This installs:
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Coverage reporting
- `ruff>=0.1.0` - Code linting
- `mypy>=1.0` - Type checking
- `pre-commit>=3.0` - Git hooks

### Recommended Backends

For best performance with datetime and number extraction:

```bash
pip install ovos-date-parser ovos-number-parser quantulum3
```

**Note:** `lingua_nostra` is deprecated. Use OVOS packages instead.

---

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/OpenJarbas/simple_NER.git
cd simple_NER
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Using virtualenv
virtualenv venv
source venv/bin/activate

# Using conda
conda create -n simple_ner python=3.11
conda activate simple_ner
```

### 3. Install Package

```bash
# Install with all dependencies
pip install -e ".[dev,all]"

# Or install specific extras
pip install -e ".[dev,units,keywords]"
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

This sets up automatic linting and formatting on commit.

### 5. Verify Installation

```bash
# Run tests
pytest test/ -v

# Check linting
ruff check simple_NER/

# Run example
python examples/pipeline_example.py
```

---

## Python Version Requirements

| simple_NER Version | Python Versions |
|-------------------|-----------------|
| 0.9.x             | 3.10 - 3.13     |
| 0.8.x             | 3.10 - 3.12     |
| 0.4.x             | 3.7 - 3.9       |

---

## Platform-Specific Instructions

### Linux

```bash
# Install system dependencies (if needed)
sudo apt-get update
sudo apt-get install python3-dev python3-venv

# Install package
pip install simple_NER[all]
```

### macOS

```bash
# Install Xcode command line tools
xcode-select --install

# Install package
pip install simple_NER[all]
```

### Windows

```bash
# Ensure pip is in PATH
# Install package
pip install simple_NER[all]

# If you encounter permission errors, run as Administrator
```

### Google Colab

```python
!pip install simple_NER[all]

# Verify installation
import simple_NER
print(simple_NER.__version__)
```

### Jupyter Notebook

```python
import sys
!{sys.executable} -m pip install simple_NER[all]
```

---

## Docker Installation

### Dockerfile Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install simple_NER
RUN pip install simple_NER[all]

# Copy your code
COPY . .

# Run your script
CMD ["python", "your_script.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  ner:
    build: .
    volumes:
      - .:/app
    command: python -m simple_NER.cli --help
```

---

## Verifying Installation

### Check Version

```bash
python -c "import simple_NER; print(simple_NER.__version__)"
```

### Run Tests

```bash
pytest test/ -v
```

### Test CLI

```bash
python -m simple_NER.cli --list-annotators
```

### Quick Test

```python
from simple_NER.annotators.factory import create_pipeline

pipeline = create_pipeline(["email"])
entities = pipeline.process("Contact test@example.com")
print(f"Found {len(entities)} entities")
```

---

## Troubleshooting

### Issue: Module Not Found

```bash
# Ensure you're in the correct virtual environment
which python
which pip

# Reinstall
pip uninstall simple_NER
pip install simple_NER
```

### Issue: Dependency Conflicts

```bash
# Create fresh virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install package
pip install simple_NER[all]
```

### Issue: ovos-date-parser Not Available

If `ovos-date-parser` is not available, the library falls back to `lingua_nostra`:

```bash
# Install fallback
pip install lingua_nostra
```

Or use TemporalNER without datetime extraction:

```python
from simple_NER.annotators.temporal_ner import TemporalNER

ner = TemporalNER(extract_datetime=False, extract_duration=True)
```

### Issue: quantulum3 Installation Fails

```bash
# Install system dependencies
sudo apt-get install python3-dev

# Or install quantulum3 separately first
pip install --upgrade pip setuptools
pip install quantulum3

# Then install simple_NER
pip install simple_NER[units]
```

### Issue: Permission Denied on Windows

Run Command Prompt as Administrator:

```bash
# Right-click Command Prompt > Run as Administrator
pip install simple_NER[all]
```

Or use user installation:

```bash
pip install --user simple_NER[all]
```

### Issue: Pre-commit Hooks Fail

```bash
# Update pre-commit
pip install --upgrade pre-commit

# Reinstall hooks
pre-commit uninstall
pre-commit install

# Run manually to test
pre-commit run --all-files
```

---

## Upgrade Guide

### From v0.4.x to v0.9.x

```bash
# Uninstall old version
pip uninstall simple_NER

# Install new version
pip install simple_NER

# Install recommended backends
pip install ovos-date-parser ovos-number-parser
```

**Note:** v0.9.x is backward compatible. All old APIs still work.

### Check Installed Version

```bash
pip show simple_NER
```

---

## Uninstallation

```bash
# Uninstall package
pip uninstall simple_NER

# Remove cache directories
rm -rf ~/.simple_NER
rm -rf .ner_cache
```

---

## Next Steps

After installation:

1. **Quick Start:** See [README.md](../readme.md#quick-start)
2. **Tutorials:** See [TUTORIALS.md](TUTORIALS.md)
3. **API Reference:** See [API.md](API.md)
4. **Examples:** Run `python examples/pipeline_example.py`

---

## Getting Help

- **Documentation:** https://github.com/OpenJarbas/simple_NER/tree/main/docs
- **Issues:** https://github.com/OpenJarbas/simple_NER/issues
- **Discussions:** https://github.com/OpenJarbas/simple_NER/discussions
