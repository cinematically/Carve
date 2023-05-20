import tkinter as tk
from tkinter import filedialog, colorchooser
import json

import os
import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"carve_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.carve")

current_file = None

def log_event(event):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {event}\n"
    with open(LOG_FILE, "a") as log:
        log.write(log_entry)

def open_file():
    global current_file
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if filepath:
        current_file = filepath
        log_event(f"Opened file: {current_file}")
        with open(current_file, "r") as file:
            text.delete(1.0, tk.END)
            text.insert(tk.END, file.read())

def new_file():
    global current_file
    current_file = None
    log_event("Opened new file")
    text.delete(1.0, tk.END)

def save_file():
    global current_file
    if current_file:
        log_event(f"Saved file: {current_file}")
        with open(current_file, "w") as file:
            file.write(text.get(1.0, tk.END))
    else:
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filepath:
            current_file = filepath
            log_event(f"Saved file: {current_file}")
            with open(current_file, "w") as file:
                file.write(text.get(1.0, tk.END))

def save_as_file():
    global current_file
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if filepath:
        current_file = filepath
        log_event(f"Saved file as: {current_file}")
        with open(current_file, "w") as file:
            file.write(text.get(1.0, tk.END))

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    def choose_background_color():
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            text.config(bg=color)

    def choose_font_color():
        color = colorchooser.askcolor(title="Choose Font Color")[1]
        if color:
            text.config(fg=color)

    def choose_font():
        font = filedialog.askopenfilename(filetypes=[("Font Files", "*.ttf")])
        if font:
            text.config(font=(font, font_size.get()))

    def change_font_size(event):
        text.config(font=(font_name.get(), font_size.get()))

    def save_settings():
        settings = {
            "font_name": font_name.get(),
            "font_size": font_size.get(),
            "background_color": text.cget("background"),
            "font_color": text.cget("foreground")
        }
        with open(SETTINGS_FILE, "w") as settings_file:
            json.dump(settings, settings_file)

    def load_settings():
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as settings_file:
                settings = json.load(settings_file)
                font_name.set(settings.get("font_name", ""))
                font_size.set(settings.get("font_size", 12))
                text.config(bg=settings.get("background_color", "white"))
                text.config(fg=settings.get("font_color", "black"))

    font_name = tk.StringVar()
    font_size = tk.IntVar(value=12)

    font_label = tk.Label(settings_window, text="Font:")
    font_label.pack()

    font_entry = tk.Entry(settings_window, textvariable=font_name)
    font_entry.pack()

    font_size_label = tk.Label(settings_window, text="Font Size:")
    font_size_label.pack()

    font_size_scale = tk.Scale(settings_window, from_=8, to=48, variable=font_size, orient=tk.HORIZONTAL, command=change_font_size)
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

def on_closing():
    log_event("Application stopped")
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Simple Text Editor")

# Create a text widget
text = tk.Text(root, wrap=tk.WORD)
text.pack(fill=tk.BOTH, expand=True)

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create the File menu
file_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_as_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=on_closing)

# Create the Settings menu
settings_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Font", command=open_settings)

# Create buttons
button_frame = tk.Frame(root)
button_frame.pack()

# Log application start
log_event("Application started")

# Run the application
root.mainloop()