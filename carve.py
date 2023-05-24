import tkinter as tk
from tkinter import filedialog, colorchooser, simpledialog
import json
import os
import datetime
import re
from syntax import c_syntax_highlighting

LOG_FILE = f"carve_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
SETTINGS_FILE = "settings.carve"

class TextFunctions:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.undo_stack = []
        self.redo_stack = []

        self.text_widget.bind("<Control-z>", self.undo)
        self.text_widget.bind("<Control-y>", self.redo)
        self.text_widget.bind("<Control-f>", self.find)
        self.text_widget.bind("<Control-x>", self.cut_selected)

    def undo(self, event=None):
        if self.undo_stack:
            text_state = self.undo_stack.pop()
            self.redo_stack.append(self.text_widget.get("1.0", tk.END))
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", text_state)

    def redo(self, event=None):
        if self.redo_stack:
            text_state = self.redo_stack.pop()
            self.undo_stack.append(self.text_widget.get("1.0", tk.END))
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", text_state)

    def find(self, event=None):
        self.text_widget.tag_remove("match", "1.0", tk.END)
        search_term = simpledialog.askstring("Find", "Enter text:")
        if search_term:
            matches = 0
            start_pos = "1.0"
            while True:
                start_pos = self.text_widget.search(search_term, start_pos, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_term)}c"
                self.text_widget.tag_add("match", start_pos, end_pos)
                matches += 1
                self.text_widget.tag_config("match", foreground=self.match_foreground, background=self.match_background)
                start_pos = end_pos

    def cut_selected(self, event=None):
        self.text_widget.event_generate("<<Cut>>")

class TextEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Text Editor")

        self.current_file = None
        self.text_clones = []
        self.font_name = tk.StringVar()  # Initialize as StringVar
        self.font_size = tk.IntVar(value=12)
        self.syntax_highlighting_colors = {}

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

        self.root.bind("<Control-t>", lambda event: self.open_new_window())
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)
        self.root.bind("<Control-x>", self.cut_selected)
        self.root.bind("<Control-f>", self.find)

        self.load_settings()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.settings = self.load_settings()
        self.text_functions = TextFunctions(self.text)

    def undo(self, event=None):
        self.text_functions.undo()

    def redo(self, event=None):
        self.text_functions.redo()

    def find(self, event=None):
        self.text_functions.find()

    def cut_selected(self, event=None):
        self.text_functions.cut_selected()

    def log_event(self, event):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[Carve] [{timestamp}] {event}\n"
        with open(LOG_FILE, "a") as log:
            log.write(log_entry)

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("C Files", "*.c"), ("Lua Files", "*.lua")])
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
            filepath = filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("C Files", "*.c"), ("Text Files", "*.txt"), ("Lua Files", "*.lua")])
            if filepath:
                if not filepath.endswith((".c", ".txt", ".lua")):
                    filepath += ".c"
                self.current_file = filepath
                self.log_event(f"Saved file: {self.current_file}")
                with open(self.current_file, "w") as file:
                    file.write(self.text.get(1.0, tk.END))

    def save_as_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("C Files", "*.c"), ("Text Files", "*.txt"), ("Lua Files", "*.lua")])
        if filepath:
            if not filepath.endswith((".c", ".txt", ".lua")):
                filepath += ".c"
            self.current_file = filepath
            self.log_event(f"Saved file as: {self.current_file}")
            with open(self.current_file, "w") as file:
                file.write(self.text.get(1.0, tk.END))

    def on_closing(self):
        if self.current_file:
            self.log_event(f"Closed file: {self.current_file}")
        else:
            self.log_event("Closed new file")
        self.root.destroy()

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
            settings = {}
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
                    self.syntax_highlighting_colors = settings.get("syntax_highlighting_colors", {})
                    self.keyword_color.set(self.syntax_highlighting_colors.get("keyword", "blue"))
                    self.operator_color.set(self.syntax_highlighting_colors.get("operator", "purple"))
                    self.comment_color.set(self.syntax_highlighting_colors.get("comment", "green"))
                    self.log_event("Loaded settings")

        for item, color in self.syntax_highlighting_colors.items():
            button = tk.Button(settings_window, text=f"Choose Color for {item}", command=lambda i=item: choose_color(i))
            button.pack()

        save_button = tk.Button(settings_window, text="Save Settings", command=save_settings)
        save_button.pack()

        load_settings()

    def apply_syntax_highlighting(self):
        _, extension = os.path.splitext(self.current_file)
        syntax_rules = c_syntax_highlighting.get(extension, {})

        for item, color in syntax_rules.items():
            tags = item + "_tag"
            self.text.tag_configure(tags, foreground=self.syntax_highlighting_colors.get(item, "black"))

            self.text.tag_remove(tags, "1.0", tk.END)

            for keyword in syntax_rules[item]:
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
        settings = {}
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
        if len(self.text_clones) < 2:
            new_window = tk.Toplevel(self.root)
            new_window.title(f"Editor {len(self.text_clones) + 1}")

            text_clone = tk.Text(new_window, wrap=tk.WORD)
            text_clone.pack(fill=tk.BOTH, expand=True)
            text_clone.config(font=(self.font_name.get(), self.font_size.get()))

            self.text_clones.append(text_clone)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    editor = TextEditor()
    editor.run()
