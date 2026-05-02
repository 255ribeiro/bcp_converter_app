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

## Notes

- Keep `bundle`, `author`, and `author_email` in `pyproject.toml` updated before shipping.
- Briefcase packaging is platform-native: build on Windows for Windows, on macOS for macOS, and on Linux for Linux.

## Toga runtime troubleshooting

- If your editor shows `Import "toga" could not be resolved`, run `poetry install` and ensure VS Code is using the Poetry environment.
- Linux local runs may need GTK runtime dependencies installed by your distro package manager.
- Windows and macOS usually work after `poetry install`; use `poetry run bcp-converter` to guarantee the correct environment is used.
