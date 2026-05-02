import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os
import re

class BCPConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("BCP File Path Converter")
        self.root.geometry("700x400")

        self.file_path = None

        tk.Button(root, text="Open .bcp File", command=self.load_file).pack(pady=10)
        tk.Button(root, text="Convert to Relative Paths", command=self.convert).pack(pady=10)

        self.log = tk.Text(root, height=15, width=80)
        self.log.pack(padx=20, pady=10, fill="both", expand=True)

        # Close button (bottom-right)
        close_btn = tk.Button(root, text="Close", command=root.destroy)
        close_btn.pack(side="bottom", anchor="se", padx=10, pady=10)

    def load_file(self):
        path = filedialog.askopenfilename(title="Select .bcp File", filetypes=[("BCP files", "*.bcp")])
        if path:
            self.file_path = Path(path)
            self.log.insert(tk.END, f"Loaded: {self.file_path}\n")

    def convert(self):
        if not self.file_path:
            tk.messagebox.showerror("Error", "No file selected.")
            return

        try:
            content = self.file_path.read_text(encoding='utf-8')
            project_dir = self.file_path.parent
            new_content = content
            self.log.insert(tk.END, "Conversions:\n")

            for match in re.finditer(r'<filepath>(.*?)</filepath>', content, re.DOTALL):
                abs_path_str = match.group(1).strip()
                if abs_path_str:
                    # Normalize path separators
                    abs_path_str = abs_path_str.replace('/', '\\')
                    try:
                        # Ensure both paths are absolute and on same drive
                        rel_path = os.path.relpath(
                            os.path.abspath(abs_path_str),
                            os.path.abspath(project_dir)
                        )
                        new_content = new_content.replace(abs_path_str, rel_path)
                        self.log.insert(tk.END, f"→ {abs_path_str} → {rel_path}\n")
                    except Exception as e:
                        self.log.insert(tk.END, f"⚠️  Failed: {abs_path_str} ({e})\n")

            self.file_path.write_text(new_content, encoding='utf-8')
            self.log.insert(tk.END, "✅ Conversion complete.\n")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Processing failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BCPConverter(root)
    root.mainloop()   