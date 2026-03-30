# Contributing to simple_NER

Thank you for your interest in contributing to simple_NER! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/simple_NER.git`
3. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev,all]"
   ```

3. Install pre-commit hooks (optional but recommended):
   ```bash
   pre-commit install
   ```

## Making Changes

### Code Style

We use the following tools to maintain code quality:

- **Ruff**: For linting and formatting
- **mypy**: For type checking

Run these tools before submitting changes:

```bash
# Format code
ruff format .

# Check for issues
ruff check .

# Type check
mypy simple_NER/
```

### Type Hints

Add type hints to your code:

```python
from typing import Any, Generator

def extract_entities(text: str, as_json: bool = False) -> Generator[Entity | dict[str, Any], None, None]:
    ...
```

### Documentation

- Add docstrings to public functions and classes
- Update the README.md if you add new features
- Include examples in the `examples/` directory

## Testing

### Running Tests

Run all tests:

```bash
pytest test/ -v
```

Run with coverage:

```bash
pytest test/ --cov=simple_NER --cov-report=term-missing
```

### Writing Tests

- Write tests for new features
- Aim for good coverage of edge cases
- Follow the existing test structure
- Use descriptive test names: `test_<feature>_<scenario>_<expected_result>`

Example:

```python
class TestEmailNER:
    def test_single_email(self):
        ner = EmailNER()
        text = "my email is test@example.com"
        results = list(ner.extract_entities(text))
        assert len(results) == 1
        assert results[0].value == "test@example.com"
```

## Submitting Changes

### Commit Messages

Write clear, concise commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:

```
Add email entity extractor

- Implement EmailNER class with regex-based email detection
- Add tests for single and multiple email extraction
- Update documentation with usage examples

Closes #123
```

### Pull Request Process

1. Update the CHANGELOG.md with your changes
2. Ensure all tests pass and coverage is maintained
3. Update documentation as needed
4. Submit a pull request with a clear description
5. Request review from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have added tests that prove my fix/feature works
- [ ] All tests pass locally
- [ ] Documentation has been updated
- [ ] CHANGELOG.md has been updated
```

## Questions?

Feel free to open an issue for any questions or discussions.

Thank you for contributing! 🎉
