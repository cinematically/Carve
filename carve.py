import tkinter as tk
from tkinter import filedialog
import os
import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "application.log")
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
file_menu.add_separator()
file_menu.add_command(label="Exit", command=on_closing)

# Create buttons
button_frame = tk.Frame(root)
button_frame.pack()

new_button = tk.Button(button_frame, text="New", command=new_file)
new_button.pack(side=tk.LEFT)

open_button = tk.Button(button_frame, text="Open", command=open_file)
open_button.pack(side=tk.LEFT)

save_button = tk.Button(button_frame, text="Save", command=save_file)
save_button.pack(side=tk.LEFT)

# Log application start
log_event("Application started")

# Run the application
root.mainloop()
