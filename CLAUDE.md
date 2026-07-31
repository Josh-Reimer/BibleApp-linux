# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
python3 bible-gui-tk.py
```

Single-file Tkinter GUI, stdlib only. No build step, no test suite, no dependency manifest. Two virtualenvs are checked out but gitignored: `.venv` (3.12) and `venv` (3.14) — neither is required, system `python3` with tkinter works.

The only optional dependency is `pyobjc` (`AppKit`), used solely by `_set_dock_icon()` on macOS to set the dock icon from `black-bible.png`. It is wrapped in a bare `except`, so its absence is silent and harmless.

## Data model

The Bible is stored as 66 plaintext files in the repo root, one per book (`genesis.txt` … `revelation.txt`), plus `Bible.txt` which is the whole KJV concatenated (loaded by `go_home()` at startup — ~4.3 MB into a single `tk.Text`).

Line format inside a book file:

```
<chapter>:<verse>: <text>
```

Each book begins with a few non-verse header lines (title, book name, blank lines). Code that parses these files must tolerate them. Two consequences already baked into the code:

- `ChapterVerse.get_chap()` filters by `verse.split(":")[0] == str(chap)` — header lines have no leading number so they fall out naturally.
- `get_selected_book()` derives the chapter count from `int(lines[-1].split(':')[0])`, i.e. it assumes the **last line of every book file is a verse**. Trailing blank lines or appended notes would break the chapter dropdown.

Verse numbers are 1-based in the UI; `get_verse()` indexes `chapter[ver - 1]`.

## Book name / filename mapping

Three parallel lists must stay index-aligned:

- `books_titled` in `bible-gui-tk.py` — display names in the book combobox
- `books_file_names` in `bible-gui-tk.py` — the corresponding `.txt` filenames
- `files` in `BibleFileNames.py` — same filename list, used as the default search corpus

`get_selected_book_from_dropdown()` maps display → file purely by list position (`books_file_names[books_titled.index(...)]`), so inserting into one list without the others silently returns the wrong book.

**Misspellings are canonical.** The lists use `philipians.txt`, `eccliasiastes.txt`, `ezekial.txt`, `first_thesselonians.txt`, `second_thesselonians.txt`. Correctly-spelled duplicates (`philippians.txt`, `first_thessalonians.txt`, `second_thessalonians.txt`) also exist on disk but are **not** referenced. Don't "fix" a name in one place only; renaming requires touching both files and the data file itself.

`OT_FILES` / `NT_FILES` are slices of `books_file_names` at index 39 (Malachi/Matthew boundary) — they depend on the list staying in canonical Bible order.

## Path handling

Every data-file access goes through `_bpath(filename)`, which joins against `SCRIPT_DIR` (the directory of `bible-gui-tk.py`). This is what makes the app runnable from any cwd — new file reads should use it rather than bare relative paths.

Note the inconsistency: `get_selected_book_from_dropdown()` returns an already-absolute path, while `get_search_files()` may return either those absolute paths (scope = "Current Book") or bare filenames from `files`/`OT_FILES`/`NT_FILES`. `linearsearch()` re-wraps everything in `_bpath()`, which happens to be idempotent for absolute paths. Preserve that property if you refactor.

## Theming

`THEMES` is a dict of named palettes with a fixed key set (`bg`, `fg`, `text_bg`, `text_fg`, `entry_bg`, `entry_fg`, `btn_bg`, `sel_bg`, `sel_fg`). Adding a theme means adding one entry with **all** keys — `_theme_widget()` indexes them unconditionally.

`_theme_widget()` walks the widget tree recursively and dispatches on `winfo_class()`. Classic `tk` widgets are recolored per-class there; `ttk` widgets (Combobox, Button, Scrollbar) can't be, so they're styled through `ttk.Style()` in `apply_theme()`. `ttk.Style().theme_use("clam")` is set at import time precisely because the native macOS/Windows ttk themes ignore color overrides — don't remove it. `Toplevel` is deliberately skipped so dialogs keep native chrome.

If you add a new widget kind, it needs a branch in `_theme_widget()` (tk) or a `style.configure` call (ttk), or it will stay unthemed.

## Settings persistence

`settings.json` holds `theme`, `font_family`, `font_size` and lives at `$XDG_CONFIG_HOME/bibleapp/settings.json` (default `~/.config/bibleapp/`), resolved by `_config_path()`. It is **not** next to the script: packaged installs mount the program directory read-only, so writes there fail silently. `_config_path()` falls back to the old in-tree location only if the config dir can't be created.

`load_settings()` tries `CONFIG_FILE` then `LEGACY_CONFIG` (the old in-tree path), so existing users keep their theme on first run after upgrading; the first readable file wins and the rest are skipped. It swallows missing/corrupt files and falls back to defaults. It is called *after* `go_home()` and *before* `apply_theme()` at startup. Settings are written only when the user hits Apply/OK in the settings dialog — font-size changes from the View menu are not persisted.

## Read-only text widget

`bible_text_widget` is a real `tk.Text` (not disabled), kept read-only by `_block_text_edit()`, which returns `"break"` for every key except navigation keys and Ctrl/Cmd+C / Ctrl/Cmd+A. Disabling the widget instead would break selection and copy, which is why it's done this way.

## Helper modules

`list_and_str_ops.py`, `charEliminator.py`, and `ChapterVerse.py` all carry "DO NOT DELETE" banners. Only `ChapterVerse` is actually imported by the current GUI (`list_and_str_ops` is imported as `list`, shadowing the builtin, but unused; `charEliminator` is not imported at all). Leave them in place — the older copy of the app under `Untitled/` still uses them.

`Untitled/` is an untracked snapshot of the pre-refactor app (no themes, no settings, relative paths). It is not the live code; edits belong in the repo root.

## Flatpak packaging

`flatpak/` holds the manifest, launcher, `.desktop` entry, and AppStream metainfo. App ID is `io.github.josh_reimer.BibleApp` (Flatpak IDs can't contain hyphens, so the GitHub username's `-` becomes `_`); the `.desktop` and metainfo filenames must keep matching that ID exactly.

```bash
flatpak install -y flathub org.freedesktop.Platform//24.08 org.freedesktop.Sdk//24.08
flatpak-builder --user --install --force-clean build-dir flatpak/io.github.josh_reimer.BibleApp.yml
flatpak run io.github.josh_reimer.BibleApp
```

The runtime ships Python but **not** Tkinter, so the manifest builds Tcl, Tk, and CPython. The load-bearing detail: Python 3.12 removed `--with-tcltk-includes`/`--with-tcltk-libs` and finds Tk only via pkg-config (`tcl >= 8.5.12 tk >= 8.5.12`), which is why `PKG_CONFIG_PATH=/app/lib/pkgconfig` is set on the `python3` module and why Tcl/Tk must install their `.pc` files first. A `post-install` step runs `import tkinter` so a broken chain fails the build instead of shipping an app that can't open a window.

Files install to `/app/share/bibleapp/` (read-only), which is why settings use the XDG path above. The app module builds the working tree via `type: dir`; the Flathub copy must pin a git tag + commit instead.

`.github/workflows/flatpak.yml` builds the manifest on x86_64 and aarch64 and uploads installable `.flatpak` bundles as run artifacts — the only way to test this from a non-Linux machine. A separate fast `metadata` job runs `appstreamcli validate` and `desktop-file-validate`, which are the checks Flathub submissions most often fail.
