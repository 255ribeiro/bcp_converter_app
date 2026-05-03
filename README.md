# BCP Converter App (Standalone)

This folder is a fully separate desktop app project using:

- Poetry for dependency and environment management
- Briefcase for app packaging/distribution
- Toga as the UI framework
- Tkinter for pure Python distribution

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

1. Install Python 3 from [python.org](https://www.python.org/downloads/)
2. Run:

```bash
python bcp-converter-python-tk.py
```

Option B: `uv` (no global Python install required)

1. Install `uv`: [Astral uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)
2. Run with managed Python:

```bash
uv run --python 3.12 bcp-converter-python-tk.py
```

### Portable binaries (PyInstaller)

The release also includes download-and-run PyInstaller bundles for Windows, macOS, and Linux.

#### Windows portable bundle

- Download `bcp-converter-pyinstaller-windows.zip` from the release.
- Extract the zip file.
- Run `bcp-converter.exe`.

#### macOS portable bundle

- Download `bcp-converter-pyinstaller-macos.zip` from the release.
- Extract the zip file.
- Open `bcp-converter.app`.
- If Gatekeeper blocks the app, right-click it and choose Open once, or run:

```bash
xattr -dr com.apple.quarantine bcp-converter.app
```

#### Linux portable bundle

- Download `bcp-converter-pyinstaller-linux.zip` from the release.
- Extract the zip file.
- Mark the binary executable if needed:

```bash
chmod +x bcp-converter
```

- Run `./bcp-converter`.

- The Linux binary is built on GitHub's Ubuntu runner, so very old distributions may need the raw Python script instead.

### Portable binaries (Nuitka)

The release also includes Nuitka bundles for Windows, macOS, and Linux.
These are built from the Toga UI app entrypoint.

#### Windows Nuitka bundle

- Download `bcp-converter-nuitka-windows.zip` from the release.
- Extract the zip file.
- Run `bcp-converter.exe`.

#### macOS Nuitka bundle

- Download `bcp-converter-nuitka-macos.zip` from the release.
- Extract the zip file.
- Run `./bcp-converter` from Terminal, or open it from Finder if marked executable.

#### Linux Nuitka bundle

- Download `bcp-converter-nuitka-linux.zip` from the release.
- Extract the zip file.
- Mark the binary executable if needed:

```bash
chmod +x bcp-converter
```

- Run `./bcp-converter`.
- This bundle also includes `bcp-converter.desktop` so you can create a launcher entry.

Example launcher installation:

```bash
mkdir -p ~/.local/share/applications
cp bcp-converter.desktop ~/.local/share/applications/
```

## Toga runtime troubleshooting

- If your editor shows `Import "toga" could not be resolved`, run `poetry install` and ensure VS Code is using the Poetry environment.
- Linux local runs may need GTK runtime dependencies installed by your distro package manager.
- Windows and macOS usually work after `poetry install`; use `poetry run bcp-converter` to guarantee the correct environment is used.
