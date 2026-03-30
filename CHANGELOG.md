# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Complete example script demonstrating all features (`examples/complete_example.py`)
- Comprehensive unit tests for annotators (`test/test_annotators.py`)
- Contributing guidelines (`CONTRIBUTING.md`)
- Pre-commit hooks configuration (`.pre-commit-config.yaml`)
- Python 3.13 support

### Changed

- Updated `pyproject.toml` with comprehensive metadata and classifiers
- Modernized GitHub Actions workflows (build_tests.yml, license_tests.yml)
- Improved optional dependencies structure
- Enhanced test coverage with pytest configuration

### Fixed

- Updated dependencies to be compatible with current Python versions
- Fixed test compatibility issues

### Removed

- Deprecated Python 3.8 and 3.9 support

## [0.8.1] - 2026-03-30

### Added

- Type hints throughout the codebase
- Ruff linting configuration
- mypy type checking configuration
- pytest configuration in pyproject.toml
- Coverage reporting configuration

## [0.4.3]  - 2020-04-12

### Added

- Names Ner
    - regex for extracting Proper Nouns
    
### Changed

- Location NER confidence reduced
    - LocationNER is less confident if lowecase is enabled
    
## [0.4.1]  - 2020-03-22

### Added

- Location NER
    - tag Capital cities and Countries from wordlist

## [0.4.0]  - 2020-02-32

### Added

- Snips NER

## [0.3.1]  - 2020-02-02

Data files were missing from pip

### Fixed

- add MANIFEST.in

## [0.3.0]  - 2019-12-12

Something was messed up in pipy, jump a number for a fresh start

## [0.2.0]  - 2019-12-12

### Changed

- Transfered ownership to [OpenJarbas](https://github.com/OpenJarbas)
- Made a changelog

### Fixed

- updated deprecated mycroft_lang_utils to lingua_franca

[unreleased]: https://github.com/OpenJarbas/simple_NER/tree/dev
[0.4.3]: https://github.com/OpenJarbas/simple_NER/tree/0.4.3
[0.4.1]: https://github.com/OpenJarbas/simple_NER/tree/0.4.1
[0.4.0]: https://github.com/OpenJarbas/simple_NER/tree/0.4.0
[0.3.0]: https://github.com/OpenJarbas/simple_NER/tree/0.3.0
[0.2.0]: https://github.com/OpenJarbas/simple_NER/tree/0.2.0
