# 🤝 Contributing Guide

Thank you for your interest in contributing to the Thingsss Scraping API Service! This guide will help you get started with contributing code, reporting issues, and improving documentation.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Code](#contributing-code)
- [Reporting Issues](#reporting-issues)
- [Documentation](#documentation)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for all contributors. Please be respectful, inclusive, and professional in all interactions.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic understanding of web scraping and FastAPI
- Familiarity with async/await patterns

### Ways to Contribute

1. **Report Bugs**: Help identify and fix issues
2. **Request Features**: Suggest new functionality
3. **Improve Documentation**: Make docs clearer and more comprehensive
4. **Add Site Support**: Add support for new websites
5. **Performance Improvements**: Optimize speed and resource usage
6. **Code Improvements**: Refactor, clean up, or enhance existing code

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/thingsss-scraper.git
cd thingsss-scraper

# Add upstream remote
git remote add upstream https://github.com/reed-hub/thingsss-scraper.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If exists
```

### 3. Install Playwright

```bash
# Install Playwright browsers
python3 -m playwright install chromium

# Verify installation
python3 -m playwright --version
```

### 4. Run Tests

```bash
# Run basic tests
python3 test_deployment.py

# Run unit tests (if implemented)
pytest tests/

# Test specific functionality
curl -X POST "http://localhost:8080/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "strategy": "http"}'
```

### 5. Enable Debug Mode

```bash
# For development
export DEBUG=true
python3 main.py
```

## Contributing Code

### 1. Create Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/add-new-site-support

# Or for bug fixes
git checkout -b fix/browser-timeout-issue
```

### 2. Make Changes

Follow these guidelines:

- **Small, focused commits**: Each commit should represent a single logical change
- **Clear commit messages**: Use descriptive commit messages
- **Follow code style**: Maintain consistency with existing code
- **Add tests**: Include tests for new functionality
- **Update documentation**: Update docs for any API changes

### 3. Code Organization

When adding new features:

```python
# Add new site support
# 1. Update app/services/strategies.py
BROWSER_REQUIRED_DOMAINS.add('newsite.com')

# 2. Add extraction rules in app/services/extractors.py
if 'newsite.com' in domain:
    selectors = ['.custom-title-selector']

# 3. Add tests
# 4. Update documentation
```

### 4. Testing Your Changes

```bash
# Test locally
python3 main.py

# Test health endpoint
curl http://localhost:8080/health

# Test new functionality
curl -X POST "http://localhost:8080/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://newsite.com/product", "strategy": "browser"}'
```

## Reporting Issues

### Bug Reports

Use the following template for bug reports:

```markdown
## Bug Description
Brief description of the issue

## Environment
- Platform: Railway/Docker/Local
- Python version: 3.11
- URL being scraped: https://example.com
- Strategy used: browser/http/auto

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Logs
```
Paste relevant logs here (mask sensitive information)
```

## Configuration
```
Environment variables used (mask sensitive data)
```

## Additional Context
Any other context about the problem
```

### Feature Requests

Use this template for feature requests:

```markdown
## Feature Description
Clear description of the feature you'd like to see

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Any other context or screenshots
```

## Documentation

### Types of Documentation

1. **API Documentation**: `docs/API.md`
2. **Deployment Guide**: `docs/DEPLOYMENT.md`
3. **Troubleshooting**: `docs/TROUBLESHOOTING.md`
4. **Code Comments**: Inline documentation
5. **README**: Main project documentation

### Documentation Standards

- **Clear and Concise**: Write for users of all skill levels
- **Examples**: Include practical examples
- **Up-to-date**: Keep docs synchronized with code changes
- **Comprehensive**: Cover all features and use cases

### Writing Style

- Use clear, simple language
- Include code examples
- Use bullet points and numbered lists
- Add diagrams where helpful
- Test all code examples

## Testing

### Types of Tests

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Test response times and resource usage

### Test Structure

```python
# tests/test_extractors.py
import pytest
from app.services.extractors import DataExtractor

class TestDataExtractor:
    def setup_method(self):
        self.extractor = DataExtractor()
    
    def test_extract_title(self):
        # Test implementation
        pass
    
    def test_extract_price(self):
        # Test implementation
        pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_extractors.py

# Run with coverage
pytest --cov=app tests/

# Run integration tests
python3 test_deployment.py
```

### Test Coverage

Aim for:
- **Unit Tests**: >80% coverage
- **Critical Functions**: 100% coverage
- **New Features**: Tests required

## Code Style

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these additions:

#### Formatting

```python
# Use black for automatic formatting
black app/

# Maximum line length: 88 characters (black default)
# Use double quotes for strings
# Use trailing commas in multi-line structures
```

#### Imports

```python
# Standard library imports first
import asyncio
import time
from typing import Optional, Dict, Any

# Third-party imports
import httpx
from fastapi import FastAPI

# Local imports
from app.core.config import settings
from app.models.requests import ScrapeRequest
```

#### Type Hints

```python
# Use type hints for all function signatures
async def scrape_url(
    url: str, 
    strategy: str = "auto"
) -> Optional[Dict[str, Any]]:
    """Scrape URL with specified strategy."""
    pass
```

#### Documentation

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid parameters provided
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result['status'])
        'success'
    """
    pass
```

### Tools

```bash
# Install development tools
pip install black flake8 mypy pytest

# Format code
black app/

# Check style
flake8 app/

# Type checking
mypy app/

# Run all checks
make lint  # If Makefile exists
```

## Pull Request Process

### 1. Prepare Your PR

Before submitting:

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

```bash
# Update your branch
git fetch upstream
git rebase upstream/main

# Run final checks
python3 test_deployment.py
black app/
flake8 app/
```

### 2. Submit Pull Request

1. **Create PR**: Use GitHub web interface
2. **Fill Template**: Use the provided PR template
3. **Add Labels**: Apply appropriate labels
4. **Request Review**: Tag relevant maintainers

### 3. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts

## Related Issues
Fixes #123
Related to #456
```

### 4. Review Process

1. **Automated Checks**: CI/CD runs tests and style checks
2. **Code Review**: Maintainers review code and provide feedback
3. **Address Feedback**: Make requested changes
4. **Final Approval**: Maintainer approves and merges

### 5. After Merge

1. **Delete Branch**: Clean up feature branch
2. **Update Local**: Pull latest changes
3. **Celebrate**: You've contributed to open source! 🎉

```bash
# After merge
git checkout main
git pull upstream main
git branch -d feature/your-feature-branch
```

## Specific Contribution Areas

### Adding New Site Support

1. **Research Site Structure**
   ```bash
   # Inspect target site
   curl -I https://newsite.com/product
   # Check robots.txt
   curl https://newsite.com/robots.txt
   ```

2. **Update Strategy Configuration**
   ```python
   # app/services/strategies.py
   BROWSER_REQUIRED_DOMAINS.add('newsite.com')
   
   # Add site-specific options
   if 'newsite.com' in domain:
       options.update({
           'wait_for': '.product-details',
           'scroll_to_bottom': True
       })
   ```

3. **Add Extraction Rules**
   ```python
   # app/services/extractors.py
   if 'newsite.com' in domain:
       title_selectors = ['.product-title', 'h1.main-title']
       price_selectors = ['.price', '.cost']
   ```

4. **Test Implementation**
   ```bash
   curl -X POST "http://localhost:8080/api/v1/scrape" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://newsite.com/product", "strategy": "browser"}'
   ```

### Performance Improvements

1. **Profile Performance**
   ```python
   # Add timing measurements
   import time
   start_time = time.time()
   # ... code ...
   print(f"Operation took {time.time() - start_time:.2f}s")
   ```

2. **Optimize Database Queries** (if added)
3. **Reduce Memory Usage**
4. **Improve Concurrent Processing**

### Security Enhancements

1. **Input Validation**: Improve URL and parameter validation
2. **Rate Limiting**: Add per-client rate limiting
3. **Authentication**: Add API key support
4. **Monitoring**: Add security event logging

## Release Process

### Version Numbers

Use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number bumped
- [ ] Tag created
- [ ] Release notes written

## Getting Help

### Communication Channels

1. **GitHub Issues**: Technical questions and bug reports
2. **GitHub Discussions**: General questions and ideas
3. **Discord/Slack**: Real-time chat (if available)

### Mentorship

New contributors welcome! We're happy to help with:
- Understanding the codebase
- Choosing good first issues
- Code review and feedback
- Best practices guidance

### Good First Issues

Look for issues labeled:
- `good-first-issue`: Perfect for newcomers
- `help-wanted`: Community contributions needed
- `documentation`: Documentation improvements
- `beginner-friendly`: Simple coding tasks

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit messages
- Invited to join maintainer team (for regular contributors)

## Questions?

Don't hesitate to ask questions! We're here to help and appreciate all contributions, no matter how small.

Thank you for contributing to the Thingsss Scraping API Service! 🚀 