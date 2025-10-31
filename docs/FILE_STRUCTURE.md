
# Ultimate Media Downloader - File Structure

## Project Directory Overview


```
ULTIMATE-MEDIA-DOWNLOADER/
├── setup.py                   # Package setup
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── config.json                # Default configuration
├── ultimate_downloader.py     # Main CLI & logic
├── spotify_handler.py         # Spotify support
├── apple_music_handler.py     # Apple Music support
├── file_manager.py            # File management
├── progress_display.py        # Progress bars
├── logger.py                  # Logging
├── ui_components.py           # CLI UI components
├── ui_display.py              # UI display logic
├── ui_utils.py                # UI utilities
├── url_validator.py           # URL validation
├── platform_info.py           # Platform info
├── platform_utils.py          # Platform utilities
├── generic_downloader.py      # Generic download logic
├── youtube_scorer.py          # YouTube search scoring
├── utils.py                   # Misc utilities
├── browser_utils.py           # Browser utilities
├── cli_args.py                # CLI argument parsing
├── CONTRIBUTING.md        # Contribution guidelines
├── scripts/                   # Install/setup scripts
│   ├── install.sh             # Unix/Mac installer
│   ├── install.bat            # Windows installer
│   ├── setup.sh               # Setup script
│   ├── setup.bat              # Windows setup
│   ├── uninstall.sh           # Unix/Mac uninstaller
│   ├── uninstall.bat          # Windows uninstaller
│   ├── activate-env.sh        # Activate venv (Unix/macOS)
│   └── activate-env.bat       # Activate venv (Windows)
│
├── docs/                      # Documentation
│   ├── INDEX.md               # Documentation hub
│   ├── USAGE.md          # Quick start guide
│   ├── INSTALL.md             # Installation instructions
|   |__ ARCHITECTURE.md
│   ├── CHANGELOG.md           # Version history
│   ├── FILE_STRUCTURE.md      # File organization
│   ├── COMMAND_REFERENCE.md   # CLI options and flags
│   ├── UNINSTALL.md           # Uninstallation guide
│
├── homebrew/                  # Homebrew formula (will not work yet)
│   └── ultimate-downloader.rb # Formula for Homebrew
│
├── .github/                   # GitHub specific files
│
├── .gitignore                 # Git ignore rules
```

---

## Key Directories & Files

### `/scripts/` - Installation & Setup Scripts
- `install.sh`, `install.bat`: Main installers for Unix/Mac and Windows
- `setup.sh`, `setup.bat`: Setup scripts
- `uninstall.sh`, `uninstall.bat`: Uninstallers
- `activate-env.sh`, `activate-env.bat`: Virtual environment activation

### `/docs/` - Documentation
- User guides, API references, technical architecture, how-to guides

### `/homebrew/` - Homebrew Formula
- `ultimate-downloader.rb`: Formula for macOS Homebrew installation ( will be available soon )

### `.github/` - GitHub Files
- Reserved for workflows, issue templates, etc.

---

## File Descriptions

### Documentation
- `README.md`: Main documentation with features, installation, and usage
- `USAGE.md`: Quick command reference
- `INSTALL.md`: Installation instructions
- `CHANGELOG.md`: Version history
- `FILE_STRUCTURE.md`: File organization
- `COMMAND_REFERENCE.md`: CLI options and flags
- `CONTRIBUTING.md`: Contribution guidelines
- `UNINSTALL.md`: Uninstallation guide
- `ARCHITECTURE.md`
- `LICENSE`: MIT License

### Configuration
- `setup.py`: Package setup
- `requirements.txt`: Production dependencies
- `requirements-dev.txt`: Development dependencies
- `config.json`: Default configuration

### Source Code
- `ultimate_downloader.py`: Main CLI & logic
- `spotify_handler.py`: Spotify support
- `apple_music_handler.py`: Apple Music support
- `file_manager.py`: File management
- `progress_display.py`: Progress bars
- `logger.py`: Logging
- `ui_components.py`: CLI UI components
- `ui_display.py`: UI display logic
- `ui_utils.py`: UI utilities
- `url_validator.py`: URL validation
- `platform_info.py`: Platform info
- `platform_utils.py`: Platform utilities
- `generic_downloader.py`: Generic download logic
- `youtube_scorer.py`: YouTube search scoring
- `utils.py`: Misc utilities

---

## Navigation Tips

1. **Quick reference**: Check `USAGE.md`
2. **Installation**: Run `./scripts/install.sh`
3. **Full docs**: Read `docs/INDEX.md` and related guides
4. **Development**: See `docs/ARCHITECTURE.md`

---

## Ignored Files (.gitignore)

Commonly ignored files and directories:
- `__pycache__/` - Python cache
- `build/`, `dist/` - Build artifacts
- `*.egg-info/` - Package info
- `venv/`, `.venv/` - Virtual environments
- `downloads/` - User downloads
- `*.log` - Log files
- `.DS_Store` - System files

---

## Recent Changes

### October 2025 - Project Reorganization
- All scripts moved to `scripts/`
- Documentation organized in `docs/`
- Cleaned up root directory
- Navigation guides added
- README updated for clarity
- Project summary documents added

---

<div align="center">

**Total Project Size**: ~2 MB (excluding .git)

**Well Organized**  •  **Easy to Navigate**  •  **Professional**

[⬆ Back to Top](#ultimate-media-downloader---file-structure)

</div>
