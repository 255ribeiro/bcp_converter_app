# nuitka-project: --mode=onefile
# nuitka-project-if: {OS} == "Windows":
#    nuitka-project: --windows-disable-console
# nuitka-project-if: {OS} == "Darwin":
#    nuitka-project: --macos-create-app-bundle

import os
import re
from pathlib import Path

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class BCPConversionService:
    FILEPATH_TAG_PATTERN = re.compile(r"(<filepath>)(.*?)(</filepath>)", re.DOTALL | re.IGNORECASE)

    def convert(self, content, project_dir):
        """Yield conversion logs and emit a final result event with converted content.

        Yields dictionaries in two formats:
        - {"type": "log", "message": "..."}
        - {"type": "result", "content": "...", "converted_count": int}
        """
        yield {"type": "log", "message": "Conversions:"}

        converted_count = 0
        chunks = []
        last_index = 0

        for match in self.FILEPATH_TAG_PATTERN.finditer(content):
            chunks.append(content[last_index:match.start()])

            open_tag, inner_text, close_tag = match.groups()
            stripped = inner_text.strip()

            if not stripped:
                chunks.append(f"{open_tag}{inner_text}{close_tag}")
                last_index = match.end()
                continue

            candidate = stripped.replace("/", "\\")

            if os.path.isabs(candidate):
                try:
                    relative_path = os.path.relpath(
                        os.path.abspath(candidate),
                        os.path.abspath(project_dir),
                    )
                    converted_count += 1
                    yield {
                        "type": "log",
                        "message": f"-> {candidate} -> {relative_path}",
                    }
                    replacement = relative_path
                except Exception as exc:
                    yield {
                        "type": "log",
                        "message": f"[WARN] Failed: {candidate} ({exc})",
                    }
                    replacement = candidate
            else:
                yield {
                    "type": "log",
                    "message": f"[SKIP] Already relative: {candidate}",
                }
                replacement = candidate

            leading_spaces = len(inner_text) - len(inner_text.lstrip())
            trailing_spaces = len(inner_text) - len(inner_text.rstrip())

            if trailing_spaces == 0:
                rebuilt_inner = (" " * leading_spaces) + replacement
            else:
                rebuilt_inner = (
                    (" " * leading_spaces)
                    + replacement
                    + (" " * trailing_spaces)
                )

            chunks.append(f"{open_tag}{rebuilt_inner}{close_tag}")
            last_index = match.end()

        chunks.append(content[last_index:])
        converted_content = "".join(chunks)

        yield {
            "type": "result",
            "content": converted_content,
            "converted_count": converted_count,
        }


class BCPConverterApp(toga.App):
    def startup(self):
        self.service = BCPConversionService()
        self.file_path = None
        self.original_content = None
        self.converted_content = None

        self.main_window = toga.MainWindow(title=self.formal_name, size=(820, 520))

        self.open_button = toga.Button(
            "Load .BCP File",
            on_press=self.load_file,
            style=Pack(padding_right=8),
        )
        self.convert_button = toga.Button(
            "Convert to Relative Paths",
            on_press=self.convert,
            enabled=False,
        )

        self.count_label = toga.Label(
            "Successfully converted paths: 0",
            style=Pack(padding=(0, 20, 10, 20)),
        )

        self.log = toga.MultilineTextInput(
            value="",
            readonly=True,
            style=Pack(flex=1, padding=(0, 20, 10, 20)),
        )

        self.save_button = toga.Button(
            "Save",
            on_press=self.save,
            enabled=False,
            style=Pack(padding_right=6),
        )
        self.save_as_button = toga.Button(
            "Save As",
            on_press=self.save_as,
            enabled=False,
        )
        self.close_button = toga.Button("Close", on_press=self.close_app)

        top_actions = toga.Box(
            children=[self.open_button, self.convert_button],
            style=Pack(direction=ROW, padding=(10, 20, 8, 20)),
        )

        bottom_actions = toga.Box(
            children=[
                self.save_button,
                self.save_as_button,
                toga.Box(style=Pack(flex=1)),
                self.close_button,
            ],
            style=Pack(direction=ROW, padding=(0, 10, 10, 10)),
        )

        content = toga.Box(
            children=[top_actions, self.count_label, self.log, bottom_actions],
            style=Pack(direction=COLUMN),
        )

        self.main_window.content = content
        self.main_window.show()

    async def _show_error(self, message):
        await self.main_window.error_dialog("Error", message)

    def _append_log(self, message):
        if self.log.value:
            self.log.value = f"{self.log.value}\n{message}"
        else:
            self.log.value = message

    @staticmethod
    def _normalize_dialog_result(result):
        if result is None:
            return None
        if isinstance(result, (list, tuple)):
            return result[0] if result else None
        return result

    async def load_file(self, widget):
        result = await self.main_window.open_file_dialog(
            title="Select .BCP File",
            file_types=["bcp"],
        )
        selected = self._normalize_dialog_result(result)
        if not selected:
            return

        self.file_path = Path(selected)
        try:
            self.original_content = self.file_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.file_path = None
            self.original_content = None
            await self._show_error(f"Unable to read file: {exc}")
            return

        self.converted_content = None
        self.count_label.text = "Successfully converted paths: 0"
        self.convert_button.enabled = True
        self.save_button.enabled = False
        self.save_as_button.enabled = False
        self._append_log(f"Loaded: {self.file_path}")

    async def convert(self, widget):
        if not self.file_path or self.original_content is None:
            await self._show_error("No file selected.")
            return

        try:
            project_dir = self.file_path.parent
            self.converted_content = None
            converted_count = 0

            for event in self.service.convert(self.original_content, project_dir):
                if event["type"] == "log":
                    self._append_log(event["message"])
                elif event["type"] == "result":
                    self.converted_content = event["content"]
                    converted_count = event["converted_count"]

            self.count_label.text = f"Successfully converted paths: {converted_count}"
            self.save_button.enabled = True
            self.save_as_button.enabled = True
            self._append_log("Conversion complete in memory. Use Save or Save As.")
        except Exception as exc:
            await self._show_error(f"Processing failed: {exc}")

    async def save(self, widget):
        if not self.file_path:
            await self._show_error("No file selected.")
            return
        if self.converted_content is None:
            await self._show_error("Nothing to save. Run conversion first.")
            return

        try:
            self.file_path.write_text(self.converted_content, encoding="utf-8")
            self._append_log(f"Saved (replaced original): {self.file_path}")
        except Exception as exc:
            await self._show_error(f"Save failed: {exc}")

    async def save_as(self, widget):
        if self.converted_content is None:
            await self._show_error("Nothing to save. Run conversion first.")
            return

        result = await self.main_window.save_file_dialog(
            title="Save Converted File As",
            suggested_filename="converted.BCF",
            file_types=["BCF"],
        )
        target = self._normalize_dialog_result(result)
        if not target:
            return

        target_path = Path(target)
        if target_path.suffix.lower() != ".bcf":
            target_path = target_path.with_suffix(".BCF")

        try:
            target_path.write_text(self.converted_content, encoding="utf-8")
            self._append_log(f"Saved as: {target_path}")
        except Exception as exc:
            await self._show_error(f"Save As failed: {exc}")

    def close_app(self, widget):
        self.exit()


def main():
    return BCPConverterApp("BCP Converter", "com.example.bcpconverter")


def run():
    main().main_loop()
