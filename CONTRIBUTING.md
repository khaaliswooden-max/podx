# Contributing to PodX

Thank you for your interest in contributing to PodX! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

---

## Code of Conduct

All contributors must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for everyone.

---

## Getting Started

### Prerequisites

- Python 3.11 or later
- Git
- Virtual environment tool (venv or conda)

### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/podx.git
cd podx

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Verify setup
python scripts/validate_environment.py
pytest tests/
```

---

## Development Process

### 1. Find an Issue

- Check [GitHub Issues](https://github.com/khaaliswooden-max/podx/issues)
- Look for `good first issue` labels for beginners
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Changes

- Follow coding standards (see below)
- Write tests for new functionality
- Update documentation as needed

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat: add network handover optimization"
```

#### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples:**
```
feat(network): add predictive handover algorithm

Implements ML-based prediction for network transitions
to reduce handover latency by 30%.

Closes #123
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these additions:

- **Line length**: 100 characters maximum
- **Imports**: Use `isort` for ordering
- **Formatting**: Use `black` for code formatting
- **Type hints**: Required for all public functions

### Code Quality Tools

```bash
# Format code
black src/
isort src/

# Lint code
pylint src/
flake8 src/

# Type checking
mypy src/

# Security scanning
bandit -r src/
```

### Example Code Style

```python
"""
Module docstring explaining the purpose.
"""

from typing import Dict, List, Optional

import numpy as np

from podx.core import BaseClass


class MyClass(BaseClass):
    """
    Class docstring with description.
    
    Attributes:
        name: Description of the attribute.
        value: Another attribute description.
    """
    
    def __init__(self, name: str, value: int = 0) -> None:
        """
        Initialize MyClass.
        
        Args:
            name: The name parameter.
            value: Optional value parameter.
        """
        self.name = name
        self.value = value
    
    def process(self, data: List[float]) -> Dict[str, float]:
        """
        Process the input data.
        
        Args:
            data: List of float values to process.
            
        Returns:
            Dictionary with processed results.
            
        Raises:
            ValueError: If data is empty.
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        return {
            "mean": np.mean(data),
            "std": np.std(data),
        }
```

---

## Testing Requirements

### Test Coverage

- Minimum 80% code coverage for new code
- All public functions must have tests
- Integration tests for cross-module functionality

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run specific test file
pytest tests/unit/test_benchmark.py

# Run specific test
pytest tests/unit/test_benchmark.py::TestXdoPBenchmarkEngine::test_run_full_benchmark
```

### Writing Tests

```python
"""Tests for the benchmark module."""

import pytest
from src.benchmark.xdop_engine import XdoPBenchmarkEngine


class TestXdoPBenchmarkEngine:
    """Tests for XdoPBenchmarkEngine class."""
    
    def test_initialization(self):
        """Test engine initializes correctly."""
        engine = XdoPBenchmarkEngine()
        assert engine is not None
    
    def test_run_benchmark_returns_valid_score(self):
        """Test benchmark returns score in valid range."""
        engine = XdoPBenchmarkEngine()
        result = engine.run_full_benchmark(simulation_mode=True)
        
        assert 0 <= result.wcbi_score <= 100
    
    @pytest.mark.parametrize("domain", [
        "mobility_network",
        "energy_power",
        "reliability",
    ])
    def test_domain_benchmarks(self, domain):
        """Test individual domain benchmarks."""
        engine = XdoPBenchmarkEngine()
        result = engine.run_domain_benchmark(domain)
        
        assert result.passed is True
```

---

## Documentation

### Documentation Requirements

- All public modules, classes, and functions need docstrings
- Update README.md for user-facing changes
- Add/update docs/ files for significant features
- Include examples where helpful

### Docstring Format

We use Google-style docstrings:

```python
def function(arg1: str, arg2: int = 0) -> bool:
    """
    Short description of function.
    
    Longer description if needed, explaining the function's
    behavior in more detail.
    
    Args:
        arg1: Description of first argument.
        arg2: Description of second argument with default.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When arg1 is empty.
        TypeError: When arg2 is not an integer.
        
    Example:
        >>> function("test", 5)
        True
    """
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
Describe testing performed.

## Related Issues
Closes #123

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
```

### Review Process

1. Automated checks must pass
2. At least one maintainer approval required
3. All comments must be resolved
4. Squash merge to main branch

---

## Community

### Communication Channels

- **GitHub Discussions**: Questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Slack**: #podx-dev (request invite)
- **Monthly Meetings**: First Tuesday, 10:00 UTC

### Getting Help

- Check existing documentation
- Search closed issues
- Ask in GitHub Discussions
- Reach out on Slack

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Annual contributor spotlight

---

## License

By contributing to PodX, you agree that your contributions will be licensed under the project's license terms.

---

Thank you for contributing to PodX! Your efforts help make mobile distributed computing accessible to everyone.


