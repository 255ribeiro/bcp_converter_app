# BCP Converter App (Standalone)

This folder is a fully separate desktop app project using:
- Poetry for dependency and environment management
- Briefcase for app packaging/distribution
- Toga as the UI framework (no Tkinter)

## 1. Setup

```powershell
cd bcp_converter_app
poetry install
```

## 2. Run locally

```powershell
poetry run bcp-converter
```

or

```powershell
poetry run python -m bcp_converter
```

## 3. Build with Briefcase

Use target OS to build target bundles:

```powershell
poetry run briefcase create
poetry run briefcase build
poetry run briefcase package
```

For development iteration:

```powershell
poetry run briefcase dev
```

## 4. Install from Releases

Download assets from the GitHub Releases page for your tag.

### Windows

- Download the Windows asset from the release.
- Run the installer/package and follow the prompts.

### macOS

- Download the macOS asset from the release.
- Open the app package and move it to Applications if desired.

### Linux (Flatpak)

- Download the Flatpak bundle from the release.
- Install with Flatpak:

```bash
flatpak install --user --bundle ./<release-file>.flatpak
```

- Run the app:

```bash
flatpak run io.github.user255ribeiro.bcp_converter
```

### Pure Python (stdlib-only script)

The release also includes `bcp-converter-python-tk.py`.

Option A: Python from python.org

1. Install Python 3 from https://www.python.org/downloads/
2. Run:

```bash
python bcp-converter-python-tk.py
```

Option B: `uv` (no global Python install required)

1. Install `uv`: https://docs.astral.sh/uv/getting-started/installation/
2. Run with managed Python:

```bash
uv run --python 3.12 bcp-converter-python-tk.py
```

## Toga runtime troubleshooting

- If your editor shows `Import "toga" could not be resolved`, run `poetry install` and ensure VS Code is using the Poetry environment.
- Linux local runs may need GTK runtime dependencies installed by your distro package manager.
- Windows and macOS usually work after `poetry install`; use `poetry run bcp-converter` to guarantee the correct environment is used.
