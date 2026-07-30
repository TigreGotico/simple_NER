# Documentation Index

Choose your path based on what you need:

## I'm New to simple_NER

Start here: we'll get you up and running in 5 minutes:
- **[Getting Started](GETTING_STARTED.md)**: installation, first pipeline, common patterns, troubleshooting

Then explore:
- **[FAQ](FAQ.md)**: answers to common questions (languages, comparison to spaCy, OVOS plugin, etc.)
- **[API Reference](API.md)**: class and method documentation

## I Want to Learn by Example

We have 15+ runnable scripts for different scenarios:
- **[examples/README.md](../examples/README.md)**: indexed with descriptions (quick start, all annotators, async, custom types, OVOS plugin, multilingual, etc.)

## I Need a Complete Reference

Architecture and advanced topics:
- **[index.md](index.md)**: complete technical reference (all classes, all annotators, advanced patterns)
- **[TUTORIALS.md](TUTORIALS.md)**: step-by-step guides for specific use cases
- **[DEPENDENCIES.md](DEPENDENCIES.md)**: what simple_NER depends on and why
- **[INSTALLATION.md](INSTALLATION.md)**: detailed installation guide for different environments
- **[MIGRATION.md](MIGRATION.md)**: upgrading between versions

## I Found a Problem or Need Help

- **[FAQ.md: Troubleshooting section](FAQ.md#troubleshooting-and-common-issues)**: solutions to common problems
- **[AUDIT.md](../AUDIT.md)**: known issues and technical debt (open bugs)
- **GitHub Issues**: [report a bug or request a feature](https://github.com/TigreGotico/simple_NER/issues)

## I'm a Developer

Contributing or maintaining simple_NER:
- **[CONTRIBUTING.md](../CONTRIBUTING.md)**: development setup, testing, commit conventions
- **[AUDIT.md](../AUDIT.md)**: known issues, technical debt (with `file.py:LINE` citations)
- **[SUGGESTIONS.md](../SUGGESTIONS.md)**: proposed improvements (open and completed)

## Which Annotator Should I Use?

| I want to find... | Use this | Documentation |
|:---|:---|:---|
| **Emails** | `email` | [index.md §EmailAnnotator](index.md#emailannotator--emailner) |
| **Phone numbers** | `phone` | [index.md §PhoneAnnotator](index.md#phoneannotator) |
| **Dates, times, durations** | `temporal` | [index.md §TemporalNER](index.md#temporalner) |
| **Numbers (numeric & written)** | `numbers` | [index.md §NumberNER](index.md#numberner) |
| **Money amounts** | `currency` | [index.md §CurrencyAnnotator](index.md#currencyannotator) |

| I want to find... | Use this | Documentation |
|:---|:---|:---|
| **Countries, cities, capitals** | `locations` | [index.md §LocationNER](index.md#locationner) |
| **Person names** | `names` | [index.md §NamesNER](index.md#namesner) |
| **Company names** | `organization` | [index.md §OrganizationAnnotator](index.md#organizationannotator) |
| **URLs** | `url` | [index.md §URLAnnotator](index.md#urlannotator) |
| **#hashtags** | `hashtag` | [index.md §HashtagAnnotator](index.md#hashtagannotator) |

| I want to find... | Use this | Documentation |
|:---|:---|:---|
| **My custom list** | `lookup` | [index.md §LookUpNER](index.md#lookupner) |
| **Custom patterns** | `SimpleNER` | [index.md §SimpleNER](index.md#simplener) |

## Quick Links

- **Main README**: [../../readme.md](../readme.md)
- **GitHub**: [TigreGotico/simple_NER](https://github.com/TigreGotico/simple_NER) : source code, issues, and discussions
- **PyPI**: [simple_NER](https://pypi.org/project/simple_NER/)
- **CHANGELOG**: [../CHANGELOG.md](../CHANGELOG.md)
