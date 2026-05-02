import os
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox


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

class TkBCPConverterUI:
    def __init__(self, root, service):
        self.root = root
        self.service = service
        self.root.title("BCP File Path Converter")
        self.root.geometry("820x520")

        self.file_path = None
        self.original_content = None
        self.converted_content = None

        top_actions = tk.Frame(root)
        top_actions.pack(fill="x", padx=20, pady=(10, 8))

        self.open_button = tk.Button(top_actions, text="Load .BCP File", command=self.load_file)
        self.open_button.pack(side="left")

        self.convert_button = tk.Button(
            top_actions,
            text="Convert to Relative Paths",
            command=self.convert,
            state=tk.DISABLED,
        )
        self.convert_button.pack(side="left", padx=(8, 0))

        self.count_var = tk.StringVar(value="Successfully converted paths: 0")
        tk.Label(root, textvariable=self.count_var, anchor="w").pack(fill="x", padx=20)

        self.log = tk.Text(root, height=18, width=100)
        self.log.pack(padx=20, pady=10, fill="both", expand=True)

        actions = tk.Frame(root)
        actions.pack(side="bottom", fill="x", padx=10, pady=10)

        self.save_button = tk.Button(actions, text="Save", command=self.save, state=tk.DISABLED)
        self.save_button.pack(side="left", padx=(0, 6))

        self.save_as_button = tk.Button(actions, text="Save As", command=self.save_as, state=tk.DISABLED)
        self.save_as_button.pack(side="left")

        close_btn = tk.Button(actions, text="Close", command=root.destroy)
        close_btn.pack(side="right")

    def load_file(self):
        path = filedialog.askopenfilename(title="Select .bcp File", filetypes=[("BCP files", "*.bcp")])
        if path:
            self.file_path = Path(path)
            try:
                self.original_content = self.file_path.read_text(encoding="utf-8")
            except Exception as exc:
                messagebox.showerror("Error", f"Unable to read file: {exc}")
                self.file_path = None
                self.original_content = None
                return

            self.converted_content = None
            self.count_var.set("Successfully converted paths: 0")
            self.convert_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
            self.save_as_button.config(state=tk.DISABLED)
            self._append_log(f"Loaded: {self.file_path}")

    def _append_log(self, message):
        self.log.insert(tk.END, f"{message}\n")
        self.log.see(tk.END)

    def convert(self):
        if not self.file_path or self.original_content is None:
            messagebox.showerror("Error", "No file selected.")
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

            self.count_var.set(f"Successfully converted paths: {converted_count}")
            self.save_button.config(state=tk.NORMAL)
            self.save_as_button.config(state=tk.NORMAL)
            self._append_log("Conversion complete in memory. Use Save or Save As.")
        except Exception as exc:
            messagebox.showerror("Error", f"Processing failed: {exc}")

    def save(self):
        if not self.file_path:
            messagebox.showerror("Error", "No file selected.")
            return
        if self.converted_content is None:
            messagebox.showerror("Error", "Nothing to save. Run conversion first.")
            return

        try:
            self.file_path.write_text(self.converted_content, encoding="utf-8")
            self._append_log(f"Saved (replaced original): {self.file_path}")
        except Exception as exc:
            messagebox.showerror("Error", f"Save failed: {exc}")

    def save_as(self):
        if self.converted_content is None:
            messagebox.showerror("Error", "Nothing to save. Run conversion first.")
            return

        target = filedialog.asksaveasfilename(
            title="Save Converted File As",
            defaultextension=".BCF",
            filetypes=[("BCF files", "*.BCF"), ("All files", "*.*")],
        )
        if not target:
            return

        try:
            Path(target).write_text(self.converted_content, encoding="utf-8")
            self._append_log(f"Saved as: {target}")
        except Exception as exc:
            messagebox.showerror("Error", f"Save As failed: {exc}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TkBCPConverterUI(root, BCPConversionService())
    root.mainloop()   