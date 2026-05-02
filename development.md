# Development and Release Guide

This document explains how to develop, build, and publish releases for the BCP Converter app across Windows, macOS, and Linux.

## Quick Start

From repository root:

```powershell
cd bcp_converter_app
poetry install
poetry run bcp-converter
```

Build locally for your current OS:

```powershell
cd bcp_converter_app
poetry run briefcase create
poetry run briefcase build
poetry run briefcase package
```

UI framework:

- The app UI is implemented with Toga in `src/bcp_converter/app.py`.
- Packaging/distribution is handled by Briefcase.

## 1. Project layout

- App root: `bcp_converter_app`
- Main app code: `bcp_converter_app/src/bcp_converter/app.py`
- Poetry + Briefcase config: `bcp_converter_app/pyproject.toml`
- CI workflow: `.github/workflows/bcp-converter-briefcase.yml`

## 2. Local development

### 2.1 Prerequisites

- Python 3.12 recommended
- Poetry installed
- OS-native build tools for your platform (required by Briefcase)
- Toga runtime dependencies available in your local environment

### 2.2 Install dependencies

From repository root:

```powershell
cd bcp_converter_app
poetry install
```

### 2.3 Run app in development

```powershell
poetry run bcp-converter
```

Alternative:

```powershell
poetry run python -m bcp_converter
```

### 2.4 Local troubleshooting (Toga)

- Import errors like `Import "toga" could not be resolved` usually indicate dependencies are not installed in the active interpreter. Run `poetry install` and switch your editor interpreter to the Poetry virtual environment.
- Linux desktop runs may require GTK packages (same family used in CI setup).
- Always run via `poetry run ...` to avoid using a global Python without project dependencies.

## 3. Local packaging (single OS)

Build on the OS you are targeting.

```powershell
cd bcp_converter_app
poetry run briefcase create
poetry run briefcase build
poetry run briefcase package
```

Output will be generated in `bcp_converter_app/dist` (and intermediate data in `bcp_converter_app/build`).

## 4. CI multi-OS builds (GitHub Actions)

The workflow `.github/workflows/bcp-converter-briefcase.yml`:

- runs on `ubuntu-latest`, `windows-latest`, and `macos-latest`
- installs Poetry and dependencies
- runs Briefcase create/build/package
- uploads artifacts for each OS
- automatically creates a GitHub Release when a `v*` tag is pushed

### 4.1 Trigger build

1. Push a change under `bcp_converter_app/**`, or
2. Run manually using **Actions > Build BCP Converter (Briefcase) > Run workflow**.

### 4.2 Download artifacts

After completion:

1. Open the workflow run
2. Download each artifact:
- `bcp-converter-ubuntu-latest-dist`
- `bcp-converter-windows-latest-dist`
- `bcp-converter-macos-latest-dist`

## 5. Release process (all OS artifacts)

Use this process when publishing a new version.

### 5.1 Update version

1. Edit `bcp_converter_app/pyproject.toml`
2. Bump `[tool.poetry].version` (example: `0.1.0` -> `0.2.0`)

### 5.2 Commit and tag

```powershell
git add bcp_converter_app/pyproject.toml
# add other changed files if needed
git commit -m "release: v0.2.0"
git tag v0.2.0
git push origin main --tags
```

### 5.3 Automatic release on tag (recommended)

After pushing a tag like `v0.2.0`:

1. The workflow builds all 3 OS artifacts
2. A `Create GitHub Release` job runs automatically
3. A GitHub Release is created for that tag
4. All generated artifacts are attached to the release

This is the default release path and requires no manual upload.

Release safety guard:

- The release job validates that all three artifact folders exist (`ubuntu`, `windows`, `macos`).
- If any one is missing, the release job fails and no GitHub Release is published.

### 5.4 Validate the published release

1. Open GitHub **Actions** and verify all jobs succeeded
2. Open **Releases** and confirm tag `v0.2.0` exists
3. Check that Windows, macOS, and Linux artifacts are attached

If the release did not publish:

- Open the `Create GitHub Release` job and check the step summary first.
- The summary now includes a clear `Release Guard Failed` section with missing artifact folder names.

### 5.5 Manual fallback (if needed)

If automatic release fails due to permissions, runner issues, or packaging errors, use the manual path.

### 5.6 Build all OS artifacts in Actions (manual flow)

1. Trigger workflow manually or via push (if changes were pushed)
2. Wait for all matrix jobs to succeed
3. Download all artifacts from the run

### 5.7 Create GitHub Release and upload assets

Option A: GitHub UI

1. Go to **Releases > Draft a new release**
2. Select tag `v0.2.0`
3. Title example: `BCP Converter v0.2.0`
4. Upload packaged files from all 3 OS builds
5. Publish release

Option B: GitHub CLI (`gh`)

```powershell
# from a folder containing release assets
gh release create v0.2.0 ^
  --title "BCP Converter v0.2.0" ^
  --notes "Cross-platform release built with Briefcase." ^
  path\to\windows\asset ^
  path\to\macos\asset ^
  path\to\linux\asset
```

## 6. Recommended release checklist

- Version bumped in `pyproject.toml`
- App runs locally (`poetry run bcp-converter`)
- CI build passed on all 3 OSes
- Release guard passed (all 3 OS artifact groups present)
- Git tag in `vX.Y.Z` format was pushed
- GitHub Release created automatically or manually if fallback was required
- All OS artifacts attached to one GitHub Release
- Release notes include major changes and known limitations

## 7. Notes and constraints

- Briefcase packaging is native-per-platform. Build each target on its own OS (the matrix workflow already does this).
- Code signing/notarization is not configured yet. Add signing later if you need trusted installers.
- Before public release, update metadata values in `pyproject.toml` (`bundle`, `author`, `author_email`, `url`).
- Release troubleshooting starts in the Actions step summary for the `Validate required OS artifacts` step.
