# Homebrew Formula Setup Guide for UMD

This guide explains how to register and distribute **Ultimate Media Downloader (UMD)** as a Homebrew formula.

## Table of Contents

1. [What is a Homebrew Tap?](#what-is-a-homebrew-tap)
2. [Creating Your Tap Repository](#creating-your-tap-repository)
3. [Formula Structure](#formula-structure)
4. [Installation Methods](#installation-methods)
5. [Publishing to Official Homebrew](#publishing-to-official-homebrew)
6. [Testing Your Formula](#testing-your-formula)
7. [Updating the Formula](#updating-the-formula)
8. [Troubleshooting](#troubleshooting)

---

## What is a Homebrew Tap?

A **Homebrew Tap** is a GitHub repository containing Homebrew formulas. It allows you to distribute custom or unofficial packages without going through the official Homebrew review process.

- **Official Homebrew**: `homebrew-core` (requires strict review)
- **Your Custom Tap**: `homebrew-umd` (your own repository)

---

## Creating Your Tap Repository

### Step 1: Create a GitHub Repository

1. Go to GitHub and create a new repository
2. Name it: `homebrew-umd` (must start with `homebrew-`)
3. Add a description: "Homebrew formula for Ultimate Media Downloader"
4. Initialize with README.md

### Step 2: Set Up the Repository Structure

```bash
git clone https://github.com/YOUR_USERNAME/homebrew-umd.git
cd homebrew-umd
mkdir -p Formula
```

### Step 3: Copy the Formula File

Copy the `Formula/umd.rb` file from the main repository:

```bash
cp ../ULTIMATE-MEDIA-DOWNLOADER/Formula/umd.rb Formula/
```

### Step 4: Commit and Push

```bash
git add Formula/umd.rb
git commit -m "Initial commit: Add umd formula"
git push origin main
```

---

## Formula Structure

The `Formula/umd.rb` file contains the following key elements:

```ruby
class Umd < Formula
  # Description and metadata
  desc "Download media from 1000+ platforms with one command"
  homepage "https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER"
  
  # Source code location
  url "https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/archive/refs/tags/v2.0.4.tar.gz"
  
  # SHA256 checksum (ensures integrity)
  sha256 "5681fff5cfc9d7c9bf3b74c03c7b6906e65eb0de21ae864d96d87ea372ca0d7d"
  
  # License
  license "MIT"
  
  # Revision number (increment when formula changes, not the package)
  revision 0
  
  # Dependencies
  depends_on "python@3.11"
  depends_on "ffmpeg"
  depends_on "yt-dlp"
  
  # Installation method
  def install
    system "bash", "scripts/setup.sh"
  end
  
  # Test after installation
  test do
    system "#{bin}/umd", "--version"
  end
end
```

### Key Fields Explained

| Field | Purpose |
|-------|---------|
| `desc` | Short description (max 80 chars) |
| `homepage` | Project website |
| `url` | Download URL for the source code |
| `sha256` | Security checksum of the tarball |
| `license` | Open source license (MIT, GPL, etc.) |
| `revision` | Formula revision (not package version) |
| `depends_on` | Required dependencies |
| `def install` | Installation instructions |
| `test do` | Verification test |

---

## Installation Methods

### Method 1: Using Your Custom Tap (Recommended)

Users can install UMD from your tap with:

```bash
# Add your tap
brew tap NK2552003/umd

# Install the formula
brew install umd

# Or in one command
brew install NK2552003/umd/umd
```

### Method 2: Direct Installation (Development)

For testing before publishing:

```bash
brew install --build-from-source ./Formula/umd.rb
```

### Method 3: From GitHub URL

Users can also install directly from the formula file:

```bash
brew install --build-from-source https://raw.githubusercontent.com/NK2552003/homebrew-umd/main/Formula/umd.rb
```

---

## Publishing to Official Homebrew

If you want to publish to `homebrew/core` (official Homebrew):

### Requirements

- ✅ Widely used project (100+ stars on GitHub)
- ✅ Stable, maintainable codebase
- ✅ Active development and support
- ✅ Source code must be open source

### Steps

1. **Fork the homebrew-core repository**
   ```bash
   git clone https://github.com/Homebrew/homebrew-core.git
   cd homebrew-core
   git checkout -b add-umd
   ```

2. **Add your formula**
   ```bash
   cp ../ULTIMATE-MEDIA-DOWNLOADER/Formula/umd.rb Formula/
   ```

3. **Run Homebrew tests**
   ```bash
   brew test-bot Formula/umd.rb
   ```

4. **Create a Pull Request**
   - Push to your fork
   - Go to github.com/Homebrew/homebrew-core
   - Create a PR with your changes
   - Wait for review and feedback
   - Maintainers will merge if approved

---

## Testing Your Formula

### Local Testing

```bash
# Test formula syntax
brew audit Formula/umd.rb

# Test installation
brew install --build-from-source ./Formula/umd.rb

# Verify it works
umd --help
umd --version
```

### Using brew test-bot (Advanced)

```bash
brew test-bot Formula/umd.rb
```

### Test Installation from GitHub

```bash
# Add tap from GitHub
brew tap NK2552003/umd https://github.com/NK2552003/homebrew-umd.git

# Install
brew install umd

# Test
umd --version
```

---

## Updating the Formula

### When to Update

1. **New UMD Release**: Update version and SHA256
2. **New Dependencies**: Add to `depends_on`
3. **Installation Changes**: Modify `def install`

### Steps to Update

1. **Create a new release in main repo**
   ```bash
   cd ULTIMATE-MEDIA-DOWNLOADER
   git tag -a v2.0.5 -m "Release 2.0.5"
   git push origin v2.0.5
   ```

2. **Get new SHA256**
   ```bash
   curl -sL https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/archive/refs/tags/v2.0.5.tar.gz | shasum -a 256
   ```

3. **Update the formula**
   ```ruby
   url "https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/archive/refs/tags/v2.0.5.tar.gz"
   sha256 "NEW_SHA256_HERE"
   revision 0  # Reset revision to 0
   ```

4. **If only formula changes (not version)**
   ```ruby
   revision 1  # Increment revision
   ```

5. **Commit and push**
   ```bash
   cd homebrew-umd
   git add Formula/umd.rb
   git commit -m "Update umd to 2.0.5"
   git push origin main
   ```

---

## Troubleshooting

### Issue: SHA256 Mismatch

**Error**: `SHA256 mismatch`

**Solution**: Recalculate the hash:
```bash
curl -sL https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/archive/refs/tags/vX.X.X.tar.gz | shasum -a 256
```

### Issue: Dependency Not Found

**Error**: `Error: Invalid `depends_on` name`

**Solution**: Check available Homebrew formulas:
```bash
brew search <package_name>
brew info <package_name>
```

### Issue: Installation Fails

**Error**: `Installation failed`

**Solution**: 
1. Check error logs: `brew install umd -v`
2. Verify `setup.sh` works on macOS
3. Check Python version: `python --version`

### Issue: Command Not Found After Installation

**Error**: `umd: command not found`

**Solution**: Ensure the formula creates a symlink:
```bash
ls -la $(brew --prefix)/bin/umd
```

If missing, the `setup.sh` script needs to properly link the executable.

---

## Additional Resources

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Homebrew Developer Guide](https://docs.brew.sh/Homebrew-Development)
- [Homebrew API Documentation](https://rubydoc.brew.sh/)
- [Creating Taps](https://docs.brew.sh/Taps)

---

## Summary

### Quick Reference

| Task | Command |
|------|---------|
| Create tap repo | `mkdir homebrew-umd && cd homebrew-umd && mkdir Formula` |
| Add formula | `cp Formula/umd.rb Formula/` |
| Get SHA256 | `curl -sL https://...archive.tar.gz \| shasum -a 256` |
| Test locally | `brew install --build-from-source ./Formula/umd.rb` |
| Install from tap | `brew tap NK2552003/umd && brew install umd` |
| Update formula | Edit `Formula/umd.rb` and push to GitHub |

---

## Contact & Support

For issues or questions:
- GitHub Issues: https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/issues
- Email: NK2552003@github.com

---

**Last Updated**: December 5, 2025
**Formula Version**: v2.0.4
