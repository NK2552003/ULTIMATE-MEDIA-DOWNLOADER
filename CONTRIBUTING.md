# Contributing to Ultimate Media Downloader

First off, thank you for considering contributing to Ultimate Media Downloader! It's people like you that make this tool better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Testing Guidelines](#testing-guidelines)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
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

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

**Required Information:**
- Clear, descriptive title
- Detailed steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Relevant logs and error messages
- Screenshots if applicable

**Example Bug Report:**

```markdown
**Bug Description:**
Download fails for Spotify playlists with more than 50 tracks

**Steps to Reproduce:**
1. Run `python ultimate_downloader.py "PLAYLIST_URL" --playlist`
2. Select "Download all tracks"
3. Wait for processing

**Expected Behavior:**
All tracks should download successfully

**Actual Behavior:**
Download stops after track 50 with error: "Connection timeout"

**Environment:**
- OS: macOS 14.0
- Python: 3.11.5
- yt-dlp: 2024.3.10

**Error Log:**
```
[ERROR] Connection timeout after 60 seconds
Traceback (most recent call last):
  ...
```
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- Clear, descriptive title
- Detailed description of the proposed functionality
- Rationale (why is this needed?)
- Possible implementation approach
- Alternative solutions considered

**Example Enhancement Request:**

```markdown
**Feature Request: Add Support for Bandcamp Albums**

**Description:**
Add native support for downloading Bandcamp albums with metadata.

**Rationale:**
Many independent artists use Bandcamp. Current workaround requires manual
URL extraction for each track.

**Proposed Implementation:**
1. Detect Bandcamp URLs in `detect_platform()`
2. Extract album metadata using BeautifulSoup
3. Download tracks individually
4. Embed metadata from Bandcamp

**Alternatives:**
- Use yt-dlp's Bandcamp extractor (limited metadata)
- Third-party Bandcamp API wrapper
```

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `documentation` - Documentation improvements

### Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write or update tests
5. Update documentation
6. Submit a pull request

---

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- FFmpeg
- Virtual environment tool

### Setup Steps

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/ultimate-downloader.git
cd ultimate-downloader

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest pytest-cov black flake8 mypy pylint

# 5. Verify setup
python ultimate_downloader.py --help
```

### Development Dependencies

```bash
# Code formatting
pip install black isort

# Linting
pip install flake8 pylint

# Type checking
pip install mypy

# Testing
pip install pytest pytest-cov pytest-mock

# Documentation
pip install pdoc3 sphinx
```

---

## Pull Request Process

### Before Submitting

1. **Update your fork:**
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/ultimate-downloader.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**
   - Write clear, commented code
   - Follow style guidelines
   - Add tests for new functionality
   - Update documentation

4. **Test your changes:**
   ```bash
   # Run tests
   pytest tests/
   
   # Check code style
   black ultimate_downloader.py
   flake8 ultimate_downloader.py
   
   # Type checking
   mypy ultimate_downloader.py
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add support for Bandcamp albums"
   ```

6. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran to verify your changes

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
```

### Review Process

1. Maintainers will review your PR within 1-2 weeks
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. You'll be added to the contributors list!

---

## Style Guidelines

### Python Style Guide

We follow PEP 8 with these modifications:

```python
# Maximum line length: 120 characters
# Use double quotes for strings
# Use type hints for function parameters and returns

# Good
def download_media(url: str, quality: str = "best") -> bool:
    """Download media from URL with specified quality."""
    pass

# Bad
def download_media(url, quality="best"):
    pass
```

### Code Organization

```python
# 1. Imports (standard library, third-party, local)
import os
import sys
from pathlib import Path

import requests
from rich.console import Console

from utils import helper_function

# 2. Constants
DEFAULT_QUALITY = "best"
MAX_RETRIES = 3

# 3. Classes
class MediaDownloader:
    """Main downloader class."""
    pass

# 4. Functions
def main():
    """Entry point."""
    pass

# 5. Main execution
if __name__ == "__main__":
    main()
```

### Documentation Style

Use Google-style docstrings:

```python
def download_media(url: str, quality: str = "best", audio_only: bool = False) -> bool:
    """Download media from a URL with specified options.
    
    This function downloads media from various platforms using yt-dlp as the
    core engine. It supports multiple quality levels and format conversions.
    
    Args:
        url: The URL of the media to download.
        quality: Video quality level. Options: 'best', '1080p', '720p', etc.
            Defaults to 'best'.
        audio_only: If True, extracts audio only. Defaults to False.
    
    Returns:
        True if download was successful, False otherwise.
    
    Raises:
        ValueError: If URL is invalid or unsupported.
        DownloadError: If download fails after retries.
    
    Example:
        >>> downloader = UltimateMediaDownloader()
        >>> success = downloader.download_media(
        ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ...     quality="1080p",
        ...     audio_only=False
        ... )
        >>> print(success)
        True
    """
    pass
```

### Naming Conventions

```python
# Classes: PascalCase
class MediaDownloader:
    pass

# Functions and methods: snake_case
def download_media():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private methods: _leading_underscore
def _internal_helper():
    pass

# Variables: snake_case
download_path = "/path/to/downloads"
```

---

## Commit Message Guidelines

We follow the Conventional Commits specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat(spotify): add support for Spotify playlists with 100+ tracks"

# Bug fix
git commit -m "fix(youtube): resolve playlist extraction timeout issue"

# Documentation
git commit -m "docs: update installation instructions for Windows"

# Refactoring
git commit -m "refactor(downloader): extract metadata handling to separate class"

# Multiple changes
git commit -m "feat(platforms): add Bandcamp support

- Add Bandcamp URL detection
- Implement album metadata extraction
- Add tests for Bandcamp downloads

Closes #123"
```

---

## Testing Guidelines

### Writing Tests

```python
import pytest
from ultimate_downloader import UltimateMediaDownloader

class TestMediaDownloader:
    """Tests for UltimateMediaDownloader class."""
    
    @pytest.fixture
    def downloader(self):
        """Create a downloader instance for testing."""
        return UltimateMediaDownloader(output_dir="test_downloads")
    
    def test_detect_platform_youtube(self, downloader):
        """Test YouTube URL detection."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert downloader.detect_platform(url) == "youtube"
    
    def test_detect_platform_spotify(self, downloader):
        """Test Spotify URL detection."""
        url = "https://open.spotify.com/track/TRACK_ID"
        assert downloader.detect_platform(url) == "spotify"
    
    @pytest.mark.integration
    def test_download_youtube_video(self, downloader):
        """Integration test for YouTube download."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        success = downloader.download_media(
            url=url,
            quality="360p",  # Low quality for faster testing
            audio_only=True
        )
        assert success is True
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_downloader.py

# Run specific test
pytest tests/test_downloader.py::TestMediaDownloader::test_detect_platform_youtube

# Run with coverage
pytest --cov=ultimate_downloader tests/

# Run integration tests only
pytest -m integration

# Run and show print statements
pytest -s
```

### Test Coverage

Aim for at least 80% test coverage:

```bash
# Generate coverage report
pytest --cov=ultimate_downloader --cov-report=html tests/

# View report
open htmlcov/index.html
```

---

## Adding New Features

### Feature Development Checklist

- [ ] Create an issue describing the feature
- [ ] Get feedback from maintainers
- [ ] Create a feature branch
- [ ] Implement the feature
- [ ] Add comprehensive tests
- [ ] Update documentation
- [ ] Add usage examples
- [ ] Update CHANGELOG.md
- [ ] Submit pull request

### Platform Support Template

When adding support for a new platform:

```python
def _download_newplatform_track(self, url: str) -> bool:
    """Download track from NewPlatform.
    
    Args:
        url: NewPlatform track URL
        
    Returns:
        True if download successful
        
    Example:
        >>> downloader._download_newplatform_track(
        ...     "https://newplatform.com/track/123"
        ... )
        True
    """
    try:
        # 1. Extract metadata
        metadata = self._extract_newplatform_metadata(url)
        
        # 2. Build search query
        search_query = f"{metadata['artist']} - {metadata['title']}"
        
        # 3. Search YouTube
        youtube_url = self._search_youtube(search_query)
        
        # 4. Download from YouTube
        return self.download_media(
            url=youtube_url,
            audio_only=True,
            add_metadata=True
        )
        
    except Exception as e:
        self.print_rich(f"[red]Error: {e}[/red]")
        return False
```

---

## Documentation Guidelines

### Code Comments

```python
# Good: Explain WHY, not WHAT
# Retry download because of intermittent network issues
retry_count = 3

# Bad: Obvious comment
# Set retry count to 3
retry_count = 3
```

### README Updates

When adding features, update:
- Features section
- Usage examples
- Command-line options table
- Supported platforms list

### API Documentation

Update DOCUMENTATION.md with:
- New class/method descriptions
- Parameter documentation
- Return value documentation
- Usage examples
- Error handling information

---

## Community

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Discord**: Real-time chat (if available)

### Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

Don't hesitate to ask! We're here to help:
- Open an issue with the `question` label
- Start a discussion on GitHub Discussions
- Contact maintainers directly

Thank you for contributing! 🎉
