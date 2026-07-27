# Auto-Update System Documentation

## Overview

Ultimate Media Downloader now includes an automatic update system that checks for new versions every time you run the application. This ensures you always have the latest features, bug fixes, and improvements.

## How It Works

### Automatic Version Checking

Every time you run `umd`, the application:

1. **Checks Current Version**: Reads your installed version
2. **Fetches Latest Version**: Queires Codeberg for the latest release
3. **Compares Versions**: Determines if an update is available
4. **Prompts for Update**: If a newer version exists, asks if you want to update
5. **Auto-Updates**: Downloads and installs the latest version with your permission

### Caching System

To avoid unnecessary network requests:
- Version information is cached for **1 hour**
- Cache is stored in `~/.umd_version_cache.json`
- Cache is automatically cleared after successful updates

## Usage

### Automatic Updates (Default Behavior)

When you run `umd`, the version checker runs automatically:

```bash
umd https://youtube.com/watch?v=example
```

If an update is available, you'll see:

```
⚠️  New version available: v3.1.0 (current: v3.0.0)
Would you like to update now? (Y/n):
```

- Press `Y` or `Enter` to update immediately
- Press `N` to skip the update and continue

### Manual Update

You can manually update at any time using the standalone scripts:

**macOS/Linux:**
```bash
cd /path/to/umd
./scripts/update.sh
```

**Windows:**
```cmd
cd C:\path\to\umd
scripts\update.bat
```

### Update via pip

You can also update directly using pipx (recommended) or pip:

**Using pipx (recommended - matches installation method):**
```bash
pipx install git+https://codeberg.org/nk2552003/umd.git --force
```

**Using pip:**
```bash
pip install --upgrade git+https://codeberg.org/nk2552003/umd.git
```

## Features

### Cross-Platform Support

✅ **Windows**: Full support with `.bat` script  
✅ **macOS**: Full support with `.sh` script  
✅ **Linux**: Full support with `.sh` script  

### Smart Update Detection

- Uses semantic versioning (e.g., 2.2.1 → 2.3.0)
- Only prompts when a newer version is available
- Handles version parsing errors gracefully

### Non-Intrusive

- Silent when no update is available
- Minimal disruption to user experience
- Fails gracefully without breaking the main application

### Update Cache

- Reduces API calls to Codeberg
- Configurable cache duration (default: 1 hour)
- Automatically refreshed after updates

## Configuration

### Disable Auto-Update Prompts

If you want to disable the automatic update check, you can modify the code:

**Option 1**: Comment out the version check in [ultimate_downloader.py](../ultimate_downloader.py#L3718):

```python
def main():
    # from version_checker import check_for_updates
    # check_for_updates(auto_update=True)
    
    args = parse_arguments()
    # ... rest of code
```

**Option 2**: Set `auto_update=False`:

```python
check_for_updates(auto_update=False)  # Only shows message, doesn't prompt
```

### Change Cache Duration

Edit [version_checker.py](../version_checker.py) and modify:

```python
self.cache_duration = 3600  # Change to desired seconds
```

Examples:
- `1800` = 30 minutes
- `3600` = 1 hour (default)
- `86400` = 24 hours

## Troubleshooting

### Update Fails

If the automatic update fails:

1. **Check Internet Connection**: Ensure you can access Codeberg
2. **Check Permissions**: You may need administrator/sudo privileges
3. **Use Manual Update**: Run the standalone update script
4. **Use pip Directly**: `pip install --upgrade git+https://codeberg.org/nk2552003/umd.git`

### Version Check Fails

If version checking fails:
- The application continues normally without interruption
- Check your internet connection
- Codeberg API may be rate-limited (rare)
- Cache will be used if available

### Cache Issues

To clear the version cache:

**macOS/Linux:**
```bash
rm ~/.umd_version_cache.json
```

**Windows:**
```cmd
del %USERPROFILE%\.umd_version_cache.json
```

## Technical Details

### Version Checker Components

- **version_checker.py**: Main update logic
- **scripts/update.sh**: Standalone update script for Unix systems
- **scripts/update.bat**: Standalone update script for Windows

### Dependencies

- `packaging`: For semantic version parsing
- `requests`: For Codeberg API calls
- Standard library modules for OS detection and caching

### Codeberg API

- Endpoint: `https://codeberg.org/api/v1/repos/{self.repo}/releases/latest`
- Rate limit: 60 requests/hour (unauthenticated)
- Cached responses minimize API calls

## Security

- Only downloads from official Codeberg repository
- Uses HTTPS for all connections
- Verifies versions before updating
- No automatic installation without user consent

## Best Practices

1. **Keep Updated**: Always accept updates for latest features and security fixes
2. **Backup Config**: Your config files are preserved during updates
3. **Check Release Notes**: Review changes in new versions
4. **Report Issues**: If updates fail, report on Codeberg

## Related Files

- [version_checker.py](../version_checker.py) - Main update logic
- [ultimate_downloader.py](../ultimate_downloader.py) - Integration point
- [scripts/update.sh](../scripts/update.sh) - Unix update script
- [scripts/update.bat](../scripts/update.bat) - Windows update script
- [requirements.txt](../requirements.txt) - Dependencies including `packaging`

## FAQ

**Q: How often does it check for updates?**  
A: Once per hour, with results cached to minimize API calls.

**Q: Can I disable automatic updates?**  
A: Yes, see the Configuration section above.

**Q: Will I lose my settings during update?**  
A: No, your config files and downloads are preserved.

**Q: What if I don't want to update right away?**  
A: Press 'N' when prompted and continue using your current version.

**Q: Can I update manually?**  
A: Yes, use the standalone update scripts or pip install command.

**Q: What happens if Codeberg is down?**  
A: The app continues normally using cached version info or assuming current version is latest.

## Support

For issues or questions about the update system:
- Open an issue on CodeBerg
- Check existing issues for similar problems
- Include error messages and your OS version
