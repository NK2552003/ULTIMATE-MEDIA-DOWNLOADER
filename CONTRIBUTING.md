# Contributing to Ultimate Media Downloader

Thank you for your interest in contributing to Ultimate Media Downloader! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Bug Report Template:**

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With URL '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- App Version: [e.g., 2.0.0]

**Logs**
```
Paste relevant log output here
```

**Additional Context**
Add any other context about the problem.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**Enhancement Template:**

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Why would this feature be useful? What problem does it solve?

**Proposed Solution**
How you envision this feature working.

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Screenshots, mockups, or examples from other projects.
```

### Adding Platform Support

Want to add support for a new platform?

1. Create a new handler class in `ultimate_downloader.py`
2. Implement the `PlatformHandler` interface
3. Add platform detection logic
4. Write tests
5. Update documentation

**Example:**

```python
class NewPlatformHandler(PlatformHandler):
    def can_handle(self, url: str) -> bool:
        return 'newplatform.com' in url
    
    def download(self, url: str, options: dict) -> Result:
        # Implementation
        pass
```

### Code Contributions

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Update documentation
6. Submit a pull request

---

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- FFmpeg
- Virtual environment tool

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ULTIMATE-MEDIA-DOWNLOADER.git
cd ULTIMATE-MEDIA-DOWNLOADER

# Add upstream remote
git remote add upstream https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

Create `requirements-dev.txt`:

```
# Testing
pytest>=7.4.3
pytest-cov>=4.1.0
pytest-mock>=3.12.0
pytest-asyncio>=0.21.1

# Code Quality
black>=23.12.0
flake8>=6.1.0
pylint>=3.0.3
mypy>=1.7.1
isort>=5.13.2

# Documentation
sphinx>=7.2.6
sphinx-rtd-theme>=2.0.0

# Pre-commit
pre-commit>=3.6.0
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line Length**: 100 characters (not 79)
- **Quotes**: Double quotes for strings
- **Indentation**: 4 spaces (no tabs)
- **Naming**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

### Code Formatting

We use **Black** for automatic formatting:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Linting

We use **Flake8** for linting:

```bash
# Run linter
flake8 .

# Configuration in .flake8
[flake8]
max-line-length = 100
exclude = venv,.git,__pycache__
ignore = E203,W503
```

### Type Hints

Use type hints for better code clarity:

```python
from typing import List, Optional, Dict, Any

def download_video(
    url: str,
    quality: Optional[str] = None,
    output_dir: Path = Path("downloads")
) -> Dict[str, Any]:
    """
    Download video from URL.
    
    Args:
        url: Video URL
        quality: Desired quality (e.g., "1080p")
        output_dir: Output directory path
        
    Returns:
        Dictionary containing download result info
        
    Raises:
        ValueError: If URL is invalid
        DownloadError: If download fails
    """
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    Brief description of function.
    
    More detailed description if needed. Can span
    multiple lines.
    
    Args:
        param1: Description of param1
        param2: Description of param2. Defaults to 0.
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is negative
        
    Example:
        >>> example_function("test", 5)
        True
    """
    pass
```

### Import Organization

Use **isort** to organize imports:

```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import requests
from rich.console import Console

# Local application imports
from .handlers import YouTubeHandler
from .utils import parse_url
```

---

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no code change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(youtube): Add support for YouTube Shorts

Implement handler for YouTube Shorts URLs. Includes:
- Detection of Shorts URLs
- Extraction of video ID
- Format selection for mobile videos

Closes #123
```

```
fix(spotify): Resolve authentication token expiry

Fix issue where cached tokens weren't refreshed properly.
Now checks token expiry before each request.

Fixes #456
```

### Commit Best Practices

- Keep commits atomic (one logical change per commit)
- Write clear, descriptive messages
- Reference issues when applicable
- Use present tense ("Add feature" not "Added feature")
- Limit subject line to 50 characters
- Wrap body at 72 characters

---

## Pull Request Process

### Before Submitting

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**:
   ```bash
   pytest tests/
   ```

3. **Check code quality**:
   ```bash
   black --check .
   flake8 .
   mypy .
   ```

4. **Update documentation**:
   - Update README if needed
   - Add docstrings
   - Update CHANGELOG.md

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update

## Testing
Describe tests you've added or run:
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
- [ ] Dependent changes merged

## Related Issues
Closes #(issue number)

## Screenshots (if applicable)
Add screenshots for UI changes
```

### Review Process

1. Automated checks must pass
2. At least one maintainer approval required
3. All review comments addressed
4. No merge conflicts
5. Documentation updated

### After Approval

- Maintainer will merge your PR
- Delete your feature branch
- Update your fork:
  ```bash
  git checkout main
  git pull upstream main
  ```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/
│   ├── test_url_parser.py
│   ├── test_handlers.py
│   └── test_utils.py
├── integration/
│   ├── test_youtube_download.py
│   └── test_spotify_download.py
└── fixtures/
    └── sample_data.json
```

### Writing Tests

```python
import pytest
from ultimate_downloader import UltimateDownloader

class TestYouTubeHandler:
    @pytest.fixture
    def downloader(self):
        """Create downloader instance for testing."""
        return UltimateDownloader()
    
    def test_youtube_url_detection(self, downloader):
        """Test YouTube URL detection."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert downloader.can_handle_youtube(url)
    
    def test_invalid_url(self, downloader):
        """Test handling of invalid URLs."""
        with pytest.raises(ValueError):
            downloader.download("not_a_url")
    
    @pytest.mark.integration
    def test_download_video(self, downloader, tmp_path):
        """Integration test for video download."""
        url = "https://www.youtube.com/watch?v=test"
        result = downloader.download(url, output_dir=tmp_path)
        assert result.success
        assert result.file_path.exists()
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_handlers.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest -m integration
```

### Mocking External Services

```python
from unittest.mock import Mock, patch

def test_youtube_api_call(self):
    """Test YouTube API call with mocked response."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {
            'title': 'Test Video',
            'url': 'http://example.com/video.mp4'
        }
        
        result = download_video('test_url')
        assert result['title'] == 'Test Video'
```

---

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Include examples in docstrings
- Keep comments up to date with code changes
- Explain "why" not just "what"

### README Updates

When adding new features, update:

- Feature list
- Usage examples
- Command-line options
- Configuration options

### Changelog

Update `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- New platform support for XYZ
- Configuration option for ABC

### Changed
- Improved error handling in download process

### Fixed
- Bug in playlist processing
```

### Documentation Site

For major features, add detailed guides:

```
docs/
├── guides/
│   ├── spotify-setup.md
│   ├── proxy-configuration.md
│   └── advanced-usage.md
└── api/
    └── handlers-api.md
```

---

## Release Process

(For Maintainers)

1. Update version in `__version__`
2. Update CHANGELOG.md
3. Create release branch
4. Tag release: `git tag -a v2.1.0 -m "Release 2.1.0"`
5. Push tags: `git push --tags`
6. Create GitHub release
7. Update documentation

---

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: File an issue with bug report template
- **Features**: Open an issue with feature request template
- **Chat**: Join our community (link TBD)

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

Thank you for contributing! 🎉

---

**Last Updated**: October 2, 2025  
**Version**: 2.0.0
