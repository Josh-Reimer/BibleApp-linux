import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *
import re
import os
import json
import ChapterVerse
import list_and_str_ops as list
from BibleFileNames import files

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def _bpath(filename):
    """Return an absolute path to a Bible data file."""
    return os.path.join(SCRIPT_DIR, filename)

window = tk.Tk()
window.title("Desktop Bible")

def _set_dock_icon():
    try:
        from AppKit import NSApplication, NSImage
        import os
        _ns_app = NSApplication.sharedApplication()
        _icon = NSImage.alloc().initWithContentsOfFile_(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "black-bible.png")
        )
        _ns_app.setApplicationIconImage_(_icon)
    except Exception:
        pass

books_titled = ["Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","First Samuel","Second Samuel","First Kings","Second Kings","First Chronicles","Second Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Eccliasiastes","Song Of Solomon","Isaiah","Jeremiah","Lamentations","Ezekial","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi","Matthew","Mark","Luke","John","Acts","Romans","First Corinthians","Second Corinthians","Galatians","Ephesians","Philipians","Colossians","First Thesselonians","Second Thesselonians","First Timothy","Second Timothy","Titus","Philemon","Hebrews","James","First Peter","Second Peter","First John","Second John","Third John","Jude","Revelation"]
books_file_names = ["genesis.txt", "exodus.txt", "leviticus.txt", "numbers.txt", "deuteronomy.txt", "joshua.txt", "judges.txt", "ruth.txt", "first_samuel.txt", "second_samuel.txt", "first_kings.txt", "second_kings.txt", "first_chronicles.txt", "second_chronicles.txt", "ezra.txt", "nehemiah.txt", "esther.txt", "job.txt", "psalms.txt", "proverbs.txt", "eccliasiastes.txt", "song_of_solomon.txt", "isaiah.txt", "jeremiah.txt", "lamentations.txt", "ezekial.txt", "daniel.txt", "hosea.txt", "joel.txt", "amos.txt", "obadiah.txt", "jonah.txt", "micah.txt", "nahum.txt", "habakkuk.txt", "zephaniah.txt", "haggai.txt", "zechariah.txt", "malachi.txt", "matthew.txt", "mark.txt", "luke.txt", "john.txt", "acts.txt", "romans.txt", "first_corinthians.txt", "second_corinthians.txt", "galatians.txt", "ephesians.txt", "philipians.txt", "colossians.txt", "first_thesselonians.txt", "second_thesselonians.txt", "first_timothy.txt", "second_timothy.txt", "titus.txt", "philemon.txt", "hebrews.txt", "james.txt", "first_peter.txt", "second_peter.txt", "first_john.txt", "second_john.txt", "third_john.txt", "jude.txt", "revelation.txt"]

OT_FILES = books_file_names[:39]   # Genesis – Malachi
NT_FILES = books_file_names[39:]   # Matthew – Revelation

# ── Themes ───────────────────────────────────────────────────────────────────
THEMES = {
    "Light": {
        "bg":        "#f0f0f0",
        "fg":        "#000000",
        "text_bg":   "#ffffff",
        "text_fg":   "#000000",
        "entry_bg":  "#ffffff",
        "entry_fg":  "#000000",
        "btn_bg":    "#a8a8a8",
        "sel_bg":    "#0078d7",
        "sel_fg":    "#ffffff",
    },
    "Dark": {
        "bg":        "#2d2d2d",
        "fg":        "#e0e0e0",
        "text_bg":   "#1e1e1e",
        "text_fg":   "#e0e0e0",
        "entry_bg":  "#3c3c3c",
        "entry_fg":  "#e0e0e0",
        "btn_bg":    "#3c3c3c",
        "sel_bg":    "#264f78",
        "sel_fg":    "#ffffff",
    },
    "Sepia": {
        "bg":        "#f0e6c8",
        "fg":        "#4a3728",
        "text_bg":   "#fdf6e3",
        "text_fg":   "#4a3728",
        "entry_bg":  "#fdf6e3",
        "entry_fg":  "#4a3728",
        "btn_bg":    "#c8a050",
        "sel_bg":    "#8b6914",
        "sel_fg":    "#ffffff",
    },
    "High Contrast": {
        "bg":        "#000000",
        "fg":        "#ffffff",
        "text_bg":   "#000000",
        "text_fg":   "#ffff00",
        "entry_bg":  "#000000",
        "entry_fg":  "#ffffff",
        "btn_bg":    "#1a1a1a",
        "sel_bg":    "#ffff00",
        "sel_fg":    "#000000",
    },
}

# ── Settings state ────────────────────────────────────────────────────────────
_font_family   = tk.StringVar(value="TkDefaultFont")
_font_size     = tk.IntVar(value=11)
_current_theme = tk.StringVar(value="Light")

CONFIG_FILE = _bpath("settings.json")

def load_settings():
    try:
        with open(CONFIG_FILE) as f:
            s = json.load(f)
        if s.get("theme") in THEMES:
            _current_theme.set(s["theme"])
        if s.get("font_family"):
            _font_family.set(s["font_family"])
        if isinstance(s.get("font_size"), int):
            _font_size.set(s["font_size"])
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass  # first run or corrupt file — use defaults

def save_settings():
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "theme":       _current_theme.get(),
                "font_family": _font_family.get(),
                "font_size":   _font_size.get(),
            }, f, indent=2)
    except OSError:
        pass

# Use "clam" so ttk widget colors are fully overridable on all platforms
ttk.Style().theme_use("clam")

# ── Frames ───────────────────────────────────────────────────────────────────
search_frame = tk.Frame(window)
search_frame.pack(fill=tk.X)

nav_frame = tk.Frame(window)
nav_frame.pack(fill=tk.X)

text_frame = tk.Frame(window)
text_frame.pack(fill=tk.BOTH, expand=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
def clean(s):
    return s.replace("_", " ").split(".")[0].title()

def hasonlyspaces(string):
    return not string or string.isspace()

def update_bible_text_widget(text):
    bible_text_widget.delete("1.0", "end")
    bible_text_widget.insert(tk.END, text)

def apply_font():
    bible_text_widget.config(font=(_font_family.get(), _font_size.get()))

# ── Theme engine ──────────────────────────────────────────────────────────────
def _theme_widget(w, t):
    cls = w.winfo_class()
    if cls == "Toplevel":
        return  # leave dialogs with native system appearance
    try:
        if cls in ("Frame", "Tk"):
            w.config(bg=t["bg"])
        elif cls == "Label":
            w.config(bg=t["bg"], fg=t["fg"])
        elif cls == "Entry":
            w.config(bg=t["entry_bg"], fg=t["entry_fg"],
                     insertbackground=t["fg"],
                     selectbackground=t["sel_bg"], selectforeground=t["sel_fg"])
        elif cls == "Checkbutton":
            w.config(bg=t["bg"], fg=t["fg"],
                     activebackground=t["bg"], activeforeground=t["fg"],
                     selectcolor=t["bg"])
        elif cls == "Text":
            w.config(bg=t["text_bg"], fg=t["text_fg"],
                     insertbackground=t["fg"],
                     selectbackground=t["sel_bg"], selectforeground=t["sel_fg"])
        elif cls == "Spinbox":
            w.config(bg=t["entry_bg"], fg=t["entry_fg"],
                     insertbackground=t["fg"], buttonbackground=t["btn_bg"])
    except tk.TclError:
        pass
    for child in w.winfo_children():
        _theme_widget(child, t)

def apply_theme(theme_name=None, target=None):
    if theme_name:
        _current_theme.set(theme_name)
    t = THEMES[_current_theme.get()]

    style = ttk.Style()
    style.configure("TCombobox",
        fieldbackground=t["entry_bg"], foreground=t["entry_fg"],
        background=t["btn_bg"], selectbackground=t["entry_bg"],
        selectforeground=t["entry_fg"], arrowcolor=t["fg"])
    style.map("TCombobox",
        fieldbackground=[("readonly", t["entry_bg"])],
        foreground=[("readonly", t["entry_fg"])],
        selectbackground=[("readonly", t["entry_bg"])],
        selectforeground=[("readonly", t["entry_fg"])],
        background=[("readonly", t["btn_bg"])])
    style.configure("TScrollbar", background=t["btn_bg"], troughcolor=t["bg"])
    style.configure("TButton",
        background=t["btn_bg"], foreground=t["fg"],
        focuscolor=t["bg"], relief="flat", padding=4)
    style.map("TButton",
        background=[("active", t["sel_bg"]), ("pressed", t["sel_bg"])],
        foreground=[("active", t["sel_fg"]), ("pressed", t["sel_fg"])])

    _theme_widget(target or window, t)
    apply_font()

# ── Context menu ─────────────────────────────────────────────────────────────
def show_context_menu(event):
    t = THEMES[_current_theme.get()]
    widget = event.widget
    menu = tk.Menu(window, tearoff=0,
                   bg=t["btn_bg"], fg=t["fg"],
                   activebackground=t["sel_bg"], activeforeground=t["sel_fg"])
    menu.add_command(label="Cut",   command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_command(label="Copy",  command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
    menu.tk_popup(event.x_root, event.y_root)

# ── Settings dialog ──────────────────────────────────────────────────────────
def open_settings():
    dlg = tk.Toplevel(window)
    dlg.title("Settings")
    dlg.resizable(False, False)
    dlg.grab_set()
    dlg.columnconfigure(0, minsize=80,  weight=1)
    dlg.columnconfigure(1, minsize=110, weight=1)
    dlg.columnconfigure(2, minsize=110, weight=1)

    FONTS = ["TkDefaultFont", "Arial", "Georgia", "Times New Roman",
             "Courier New", "Helvetica", "Palatino",
             "DejaVu Sans", "DejaVu Serif", "Liberation Sans", "Liberation Serif"]

    tk.Label(dlg, text="Theme:").grid(row=0, column=0, padx=12, pady=10, sticky="w")
    tk.OptionMenu(dlg, _current_theme, *THEMES.keys()).grid(
        row=0, column=1, columnspan=2, padx=12, pady=10, sticky="ew")

    tk.Label(dlg, text="Font:").grid(row=1, column=0, padx=12, pady=10, sticky="w")
    tk.OptionMenu(dlg, _font_family, *FONTS).grid(
        row=1, column=1, columnspan=2, padx=12, pady=10, sticky="ew")

    tk.Label(dlg, text="Size:").grid(row=2, column=0, padx=12, pady=10, sticky="w")
    tk.Spinbox(dlg, from_=8, to=32, textvariable=_font_size,
               width=5).grid(row=2, column=1, padx=12, pady=10, sticky="w")

    def on_apply():
        apply_theme()
        save_settings()

    ttk.Button(dlg, text="Apply",  command=on_apply).grid(
        row=3, column=0, pady=(5, 12), padx=8)
    ttk.Button(dlg, text="OK",     command=lambda: [on_apply(), dlg.destroy()]).grid(
        row=3, column=1, pady=(5, 12), padx=8)
    ttk.Button(dlg, text="Cancel", command=dlg.destroy).grid(
        row=3, column=2, pady=(5, 12), padx=8)

# ── Menubar ──────────────────────────────────────────────────────────────────
menubar   = tk.Menu(window)
view_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="View", menu=view_menu)
view_menu.add_command(
    label="Increase Font Size",
    command=lambda: [_font_size.set(_font_size.get() + 1), apply_font()])
view_menu.add_command(
    label="Decrease Font Size",
    command=lambda: [_font_size.set(max(6, _font_size.get() - 1)), apply_font()])
view_menu.add_separator()
view_menu.add_command(label="Settings...", command=open_settings)
window.config(menu=menubar)

# ── Search toolbar ────────────────────────────────────────────────────────────
for col in range(8):
    search_frame.columnconfigure(col, weight=1, minsize=40)

searchBar_label  = tk.Label(search_frame, text="Search:")
searchBar_entry  = tk.Entry(search_frame)
clear_button     = ttk.Button(search_frame, text="Clear",
                              command=lambda: searchBar_entry.delete(0, END))
search_button    = ttk.Button(search_frame, text="Search",
                              command=lambda: search_button_event())

scope_var   = tk.StringVar(value="All Books")
scope_combo = ttk.Combobox(search_frame, textvariable=scope_var,
                            values=["All Books", "Old Testament", "New Testament", "Current Book"],
                            state="readonly", width=14)

whole_word_var   = tk.BooleanVar(value=False)
whole_word_check = tk.Checkbutton(search_frame, text="Whole word", variable=whole_word_var)

results_label = tk.Label(search_frame, text="No search results yet...")

searchBar_label.grid(  row=0, column=0, sticky="ew", padx=2, pady=3)
searchBar_entry.grid(  row=0, column=1, sticky="ew", padx=2, pady=3)
clear_button.grid(     row=0, column=2, sticky="ew", padx=2, pady=3)
search_button.grid(    row=0, column=3, sticky="ew", padx=2, pady=3)
scope_combo.grid(      row=0, column=4, sticky="ew", padx=2, pady=3)
whole_word_check.grid( row=0, column=5, sticky="ew", padx=2, pady=3)
results_label.grid(    row=0, column=6, columnspan=2, sticky="ew", padx=2, pady=3)

searchBar_entry.bind("<Return>",   lambda e: search_button_event())
searchBar_entry.bind("<Button-3>", show_context_menu)

# ── Navigation toolbar ────────────────────────────────────────────────────────
for col in range(4):
    nav_frame.columnconfigure(col, weight=1, minsize=40)

home_button = ttk.Button(nav_frame, text="Home", command=lambda: go_home())

value_inside_book_selector    = tk.StringVar(value="Select a Book")
value_inside_chapter_selecter = tk.StringVar(value="")
value_inside_verse_selecter   = tk.StringVar(value="")

book_selector_combobox    = ttk.Combobox(nav_frame, width=18,
                                          textvariable=value_inside_book_selector)
chapter_selector_combobox = ttk.Combobox(nav_frame, width=4,
                                          textvariable=value_inside_chapter_selecter)
verse_selector_combobox   = ttk.Combobox(nav_frame, width=4,
                                          textvariable=value_inside_verse_selecter)

book_selector_combobox['values']    = books_titled
chapter_selector_combobox['values'] = []
verse_selector_combobox['values']   = []

home_button.grid(              row=0, column=0, sticky="ew", padx=2, pady=3)
book_selector_combobox.grid(   row=0, column=1, sticky="ew", padx=2, pady=3)
chapter_selector_combobox.grid(row=0, column=2, sticky="ew", padx=2, pady=3)
verse_selector_combobox.grid(  row=0, column=3, sticky="ew", padx=2, pady=3)

# ── Text widget ───────────────────────────────────────────────────────────────
bible_text_widget = tk.Text(text_frame, wrap=tk.WORD, cursor="arrow")
bible_text_widget.pack(fill=tk.BOTH, expand=True)
bible_text_widget.bind("<Button-3>", show_context_menu)

def _block_text_edit(event):
    # Allow navigation, selection, and copy/select-all shortcuts
    if event.keysym in ("Left", "Right", "Up", "Down", "Home", "End",
                         "Prior", "Next", "Shift_L", "Shift_R",
                         "Control_L", "Control_R", "Meta_L", "Meta_R"):
        return
    mod = event.state
    if (mod & 0x8 or mod & 0x4) and event.keysym.lower() in ("c", "a"):
        return  # Cmd/Ctrl + C or A
    return "break"  # block all editing keys

bible_text_widget.bind("<Key>", _block_text_edit)

# ── Navigation callbacks ──────────────────────────────────────────────────────
def go_home():
    with open(_bpath("Bible.txt"), "r") as f:
        update_bible_text_widget(f.read())

def get_selected_book_from_dropdown():
    return _bpath(books_file_names[books_titled.index(book_selector_combobox.get())])

def get_selected_chapter_from_dropdown():
    return int(chapter_selector_combobox.get())

def get_selected_book(event):
    filename = get_selected_book_from_dropdown()
    with open(filename, "r") as f:
        update_bible_text_widget(f.read())
    with open(filename, "r") as f:
        lines = f.readlines()
    n_chapters = int(lines[-1].split(':')[0])
    chapter_selector_combobox['values'] = [str(i) for i in range(1, n_chapters + 1)]
    chapter_selector_combobox.set("")
    verse_selector_combobox['values'] = []
    verse_selector_combobox.set("")

def get_selected_chapter(event):
    chapter_list = ChapterVerse.get_chap(
        get_selected_book_from_dropdown(),
        get_selected_chapter_from_dropdown()
    )
    verse_selector_combobox['values'] = [str(i + 1) for i in range(len(chapter_list))]
    verse_selector_combobox.set("")
    update_bible_text_widget(" ".join(chapter_list))

def get_selected_verse(event):
    verse_text = ChapterVerse.get_verse(
        get_selected_book_from_dropdown(),
        get_selected_chapter_from_dropdown(),
        int(verse_selector_combobox.get())
    )
    update_bible_text_widget(verse_text)

book_selector_combobox.bind("<<ComboboxSelected>>",    get_selected_book)
chapter_selector_combobox.bind("<<ComboboxSelected>>", get_selected_chapter)
verse_selector_combobox.bind("<<ComboboxSelected>>",   get_selected_verse)

# ── Search ────────────────────────────────────────────────────────────────────
def get_search_files():
    scope = scope_var.get()
    if scope == "Old Testament":
        return OT_FILES
    if scope == "New Testament":
        return NT_FILES
    if scope == "Current Book":
        try:
            return [get_selected_book_from_dropdown()]
        except (ValueError, IndexError):
            return files
    return files

def search_button_event():
    word = searchBar_entry.get()
    if hasonlyspaces(word):
        return
    linearsearch(word)

def linearsearch(searchkey):
    results   = []
    key_lower = searchkey.lower()
    pattern   = re.compile(r'\b' + re.escape(key_lower) + r'\b') if whole_word_var.get() else None

    for book in get_search_files():
        with open(_bpath(book)) as f:
            verses = f.readlines()
        book_title = clean(book)
        for verse in verses:
            verse_lower = verse.lower()
            matched = bool(pattern.search(verse_lower)) if pattern else key_lower in verse_lower
            if matched:
                results.append(f"{book_title}\n{verse}")

    count = len(results)
    if count == 0:
        update_bible_text_widget(
            f"No results for '{searchkey}'. "
            "Try different keywords, spacing, or punctuation. (Search is not case-sensitive.)"
        )
        results_label.config(text=f"No results for '{searchkey}'")
    else:
        update_bible_text_widget("".join(results))
        noun = "result" if count == 1 else "results"
        results_label.config(text=f"{count} {noun} for '{searchkey}'")

# ── Startup ───────────────────────────────────────────────────────────────────
go_home()
load_settings()
apply_theme()
window.after(200, _set_dock_icon)

window.mainloop()
