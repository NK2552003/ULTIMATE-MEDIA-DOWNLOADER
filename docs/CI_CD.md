# CI/CD Guide

This project ships two GitHub Actions workflows: a lightweight CI smoke test and a release pipeline that builds OS-targeted zip bundles with Python distributions attached to tagged releases.

## Workflows

### CI (`.github/workflows/ci.yml`)

- **Triggers**: every push and pull request to `main`.
- **What it does**:
  - Installs runtime dependencies and the editable package.
  - Runs `python -m compileall .` to catch syntax errors early.
  - Runs `python ultimate_downloader.py --help` as a CLI smoke test.
- **Artifacts**: none (fast feedback only).

### Release (`.github/workflows/release.yml`)

- **Triggers**: push of a tag that matches `v*.*.*` or manual `workflow_dispatch` with a `vX.Y.Z` input.
- **Steps** (per OS matrix: Linux, macOS, Windows):
  - Validates the tag version matches `setup.py`.
  - Installs deps, byte-compiles sources, builds wheel + sdist.
  - Creates an OS-specific zip bundle containing only the relevant install scripts.
  - Uploads the bundle as an artifact; Linux also uploads the Python distributions.
- **Publish job**: downloads all artifacts and attaches them to a GitHub Release whose body is sourced from `docs/CHANGELOG.md`.

## Artifact naming and contents

- **Zip name**: `ultimate-media-downloader-<version>-<os>.zip` (os is `linux`, `macos`, or `windows`).
- **Inside each zip**:
  - Core Python modules (`*.py`), `config.json`, `requirements.txt`, `setup.py`, `LICENSE`, `README.md`.
  - Documentation directories (`docs/`, `Formula/`).
  - OS-appropriate install scripts:
    - Linux/macOS: `scripts/install.sh`, `setup.sh`, `activate-env.sh`, `uninstall.sh`.
    - Windows: `scripts/install.bat`, `setup.bat`, `activate-env.bat`, `uninstall.bat`.
  - Built Python distributions from `dist/` (wheel and sdist).

## How to cut a release

1. **Bump version** in `setup.py` and update `docs/CHANGELOG.md` under `[Unreleased]`, then commit.
2. **Tag** the commit (start at `v1.0.0` for the first release): `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. (Optional) Trigger manually via the Actions UI if you need to rebuild an existing tag.
4. **Outputs**: a GitHub Release named `Ultimate Media Downloader vX.Y.Z` with the OS zip bundles plus wheel/sdist attached.

## Local checks before pushing

- `python -m compileall .` — syntax sanity check.
- `python ultimate_downloader.py --help` — quick CLI smoke test.
- (If you add tests later) `pytest` — run unit tests.

## Versioning policy

- Uses **Semantic Versioning**: `MAJOR.MINOR.PATCH`.
- Tag names must include a leading `v` (e.g., `v2.0.1`).
- The release workflow fails if the tag and `setup.py` disagree.
