import tkinter as tk
from tkinter import filedialog, colorchooser
import json
import os
import datetime
import re

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"carve_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.carve")

c_syntax_highlighting = {
    ".c": {
        "keywords": [
            "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum",
            "extern", "float", "for", "goto", "if", "int", "long", "register", "return", "short", "signed",
            "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while"
        ],
        "operators": [
            "+", "-", "*", "/", "%", "=", "==", "!=", ">", "<", ">=", "<=", "&&", "||", "!", "&", "|", "~",
            "^", "<<", ">>"
        ],
        "comments": ["//", "/*", "*/"],
        "keyword_color": "blue",
        "operator_color": "purple",
        "comment_color": "green"
    },
    ".h": {
        "keywords": [
            "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum",
            "extern", "float", "for", "goto", "if", "int", "long", "register", "return", "short", "signed",
            "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while"
        ],
        "operators": [
            "+", "-", "*", "/", "%", "=", "==", "!=", ">", "<", ">=", "<=", "&&", "||", "!", "&", "|", "~",
            "^", "<<", ">>"
        ],
        "comments": ["//", "/*", "*/"],
        "keyword_color": "blue",
        "operator_color": "purple",
        "comment_color": "green"
    }
}

class TextEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Text Editor")

        self.current_file = None
        self.window_count = 0
        self.text_clones = []
        self.font_name = tk.StringVar()  # Initialize as StringVar
        self.font_size = tk.IntVar(value=12)
        self.syntax_highlighting_colors = {}  # Initialize syntax highlighting colors dictionary

        self.keyword_color = tk.StringVar(value="blue")
        self.operator_color = tk.StringVar(value="purple")
        self.comment_color = tk.StringVar(value="green")

        self.text = tk.Text(self.root, wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True)

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing)

        self.settings_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Font", command=self.open_settings)
        self.settings_menu.add_command(label="Syntax Highlighting", command=self.open_syntax_highlighting_settings)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()

        self.root.bind("<Control-t>", lambda event: self.open_new_window)

        self.load_settings()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log_event(self, event):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[Carve] [{timestamp}] {event}\n"
        with open(LOG_FILE, "a") as log:
            log.write(log_entry)

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("C Files", "*.c")])
        if filepath:
            self.current_file = filepath
            self.log_event(f"Opened file: {self.current_file}")
            with open(self.current_file, "r") as file:
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, file.read())
            self.apply_syntax_highlighting()

    def new_file(self):
        self.current_file = None
        self.log_event("Opened new file")
        self.text.delete(1.0, tk.END)

    def save_file(self):
        if self.current_file:
            self.log_event(f"Saved file: {self.current_file}")
            with open(self.current_file, "w") as file:
                file.write(self.text.get(1.0, tk.END))
        else:
            filepath = filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("C Files", "*.c"), ("Text Files", "*.txt")])
            if filepath:
                if not filepath.endswith((".c", ".txt")):
                    filepath += ".c"
                self.current_file = filepath
                self.log_event(f"Saved file: {self.current_file}")
                with open(self.current_file, "w") as file:
                    file.write(self.text.get(1.0, tk.END))

    def save_as_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("C Files", "*.c"), ("Text Files", "*.txt")])
        if filepath:
            if not filepath.endswith((".c", ".txt")):
                filepath += ".c"
            self.current_file = filepath
            self.log_event(f"Saved file as: {self.current_file}")
            with open(self.current_file, "w") as file:
                file.write(self.text.get(1.0, tk.END))

    def on_closing(self):
        # Log the file that was closed
        if self.current_file:
            self.log_event(f"Closed file: {self.current_file}")
        else:
            self.log_event("Closed new file")

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        def choose_background_color():
            color = colorchooser.askcolor(title="Choose Background Color")[1]
            if color:
                self.text.config(bg=color)

        def choose_font_color():
            color = colorchooser.askcolor(title="Choose Font Color")[1]
            if color:
                self.text.config(fg=color)

        def choose_font():
            font = filedialog.askopenfilename(filetypes=[("Font Files", "*.ttf")])
            if font:
                self.text.config(font=(font, self.font_size.get()))

        def change_font_size(event):
            self.text.config(font=(self.font_name.get(), self.font_size.get()))

        def save_settings():
            settings = {
                "font_name": self.font_name.get(),
                "font_size": self.font_size.get(),
                "background_color": self.text.cget("background"),
                "font_color": self.text.cget("foreground")
            }
            with open(SETTINGS_FILE, "w") as settings_file:
                json.dump(settings, settings_file, indent=4)

        def load_settings():
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r") as settings_file:
                    settings = json.load(settings_file)
                    self.font_name.set(settings.get("font_name", ""))
                    self.font_size.set(settings.get("font_size", 12))
                    self.text.config(bg=settings.get("background_color", "white"))
                    self.text.config(fg=settings.get("font_color", "black"))
                    self.log_event("Loaded settings")

        font_label = tk.Label(settings_window, text="Font:")
        font_label.pack()

        font_entry = tk.Entry(settings_window, textvariable=self.font_name)
        font_entry.pack()

        font_size_label = tk.Label(settings_window, text="Font Size:")
        font_size_label.pack()

        font_size_scale = tk.Scale(settings_window, from_=8, to=48, variable=self.font_size, orient=tk.HORIZONTAL, command=change_font_size)
        font_size_scale.pack()

        background_button = tk.Button(settings_window, text="Choose Background Color", command=choose_background_color)
        background_button.pack()

        font_color_button = tk.Button(settings_window, text="Choose Font Color", command=choose_font_color)
        font_color_button.pack()

        font_button = tk.Button(settings_window, text="Choose Font", command=choose_font)
        font_button.pack()

        save_button = tk.Button(settings_window, text="Save Settings", command=save_settings)
        save_button.pack()

        load_settings()

    def open_syntax_highlighting_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Syntax Highlighting Settings")

        self.syntax_highlighting_colors = {}

        def choose_color(item):
            color = colorchooser.askcolor(title=f"Choose Color for {item}")[1]
            if color:
                self.syntax_highlighting_colors[item] = color

        def save_settings():
            with open(SETTINGS_FILE, "r") as settings_file:
                settings = json.load(settings_file)
            settings["syntax_highlighting_colors"] = self.syntax_highlighting_colors
            with open(SETTINGS_FILE, "w") as settings_file:
                json.dump(settings, settings_file, indent=4)

        def load_settings():
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r") as settings_file:
                    settings = json.load(settings_file)
                    self.font_name.set(settings.get("font_name", ""))
                    self.font_size.set(settings.get("font_size", 12))
                    self.text.config(bg=settings.get("background_color", "white"))
                    self.text.config(fg=settings.get("font_color", "black"))
                    syntax_highlighting_colors = settings.get("syntax_highlighting_colors", {})
                    self.keyword_color.set(syntax_highlighting_colors.get("keyword", "blue") or "blue")
                    self.operator_color.set(syntax_highlighting_colors.get("operator", "purple") or "purple")
                    self.comment_color.set(syntax_highlighting_colors.get("comment", "green") or "green")
                    self.log_event("Loaded settings")
            else:
                self.keyword_color.set("blue")
                self.operator_color.set("purple")
                self.comment_color.set("green")

        for item, color in self.syntax_highlighting_colors.items():
            button = tk.Button(settings_window, text=f"Choose Color for {item}", command=lambda i=item: choose_color(i))
            button.pack()

        save_button = tk.Button(settings_window, text="Save Settings", command=save_settings)
        save_button.pack()

        load_settings()

    def apply_syntax_highlighting(self):
        _, extension = os.path.splitext(self.current_file)
        syntax_rules = c_syntax_highlighting.get(extension, {})
        for item, keywords in syntax_rules.items():
            tags = item + "_tag"
            color = self.syntax_highlighting_colors.get(item, "black")
            self.text.tag_configure(tags, foreground=color)
            for keyword in keywords:
                pattern = r"\b" + re.escape(keyword) + r"\b"
                start = "1.0"
                while True:
                    start = self.text.search(pattern, start, stopindex=tk.END, count=tk.NONE, regexp=True)
                    if not start:
                        break
                    end = f"{start} + {len(keyword)}c"
                    self.text.tag_add(tags, start, end)
                    start = end

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as settings_file:
                settings = json.load(settings_file)
                self.font_name.set(settings.get("font_name", ""))
                self.font_size.set(settings.get("font_size", 12))
                self.text.config(bg=settings.get("background_color", "white"))
                self.text.config(fg=settings.get("font_color", "black"))
                self.syntax_highlighting_colors = settings.get("syntax_highlighting_colors", {})
                self.log_event("Loaded settings")

    def open_new_window(self):
        if self.window_count < 2:
            self.window_count += 1
            new_window = tk.Toplevel(self.root)
            new_window.title(f"Editor {self.window_count}")

            text_clone = tk.Text(new_window, wrap=tk.WORD)
            text_clone.pack(fill=tk.BOTH, expand=True)
            text_clone.config(font=(self.font_name.get(), self.font_size.get()))

            self.text_clones.append(text_clone)

    def on_closing(self):
        self.log_event("Application stopped")
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    editor = TextEditor()
    editor.run()
