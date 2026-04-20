"""
Tkinter GUI (ttk-first): input, credibility feedback, fact-check launch, flag & clear.
"""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from classifier import evaluate_credibility, process_input
from data_loader import flag_new_source, last_load_error, load_datasets
from logger import sanitize_for_log
from search import execute_search

TITLE = "P.R.O.V.E."
SUBTITLE = "Python Resolve for Objective Verification & Evaluation"

_BG = "#f0f1f4"
_CARD = "#fafbfc"
_CARD_BORDER = "#e4e6eb"
_TEXT = "#141414"
_TEXT_MUTED = "#5f6368"
_STRIP_NEUTRAL = "#9aa0a6"
_STRIP_FAKE = "#d93025"
_STRIP_UGC = "#f29900"
_STRIP_UNKNOWN = "#1e8e3e"
_STRIP_ERROR = "#ea8600"

_DEFAULT_STATUS = (
    "Ready — enter a URL or a short claim, then Submit. Your browser opens a "
    "fact-check–oriented search; nothing is fetched inside this app."
)

# Selects and applies an appropriate UI theme based on the operating system (Windows, macOS, or default).
def _pick_theme(root: tk.Tk, style: ttk.Style) -> None:
    if sys.platform == "win32":
        for name in ("vista", "xpnative", "clam"):
            try:
                style.theme_use(name)
                return
            except tk.TclError:
                continue
    for name in ("aqua", "clam"):
        try:
            style.theme_use(name)
            return
        except tk.TclError:
            continue
    style.theme_use("default")

# Configures the global visual styles for various Tkinter widgets (frames, labels, buttons) used in the application.
def _setup_style(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    _pick_theme(root, style)

    style.configure("App.TFrame", background=_BG)
    style.configure(
        "Title.TLabel",
        background=_BG,
        foreground=_TEXT,
        font=("Segoe UI", 16, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=_BG,
        foreground=_TEXT_MUTED,
        font=("Segoe UI", 10),
    )
    style.configure(
        "TLabel",
        background=_BG,
        foreground=_TEXT,
        font=("Segoe UI", 10),
    )
    style.configure(
        "TEntry",
        font=("Segoe UI", 10),
        padding=(10, 8),
    )
    style.configure(
        "TButton",
        font=("Segoe UI", 10),
        padding=(14, 8),
    )
    style.map(
        "TButton",
        foreground=[("disabled", _TEXT_MUTED)],
    )
    # Slightly tighter secondary actions
    style.configure(
        "Ghost.TButton",
        font=("Segoe UI", 10),
        padding=(12, 7),
        background=_BG,
    )

    if sys.platform == "win32" and style.theme_use() == "vista":
        try:
            style.configure(
                "Accent.TButton",
                font=("Segoe UI", 10, "bold"),
                padding=(16, 9),
            )
        except tk.TclError:
            pass

    root.configure(bg=_BG)
    return style

# Determines the appropriate button style name to use for the main submit action, favoring native accent styles on Windows.
def _submit_button_style(style: ttk.Style) -> str:
    """Use Windows accent primary when the theme supports it."""
    if sys.platform == "win32" and style.theme_use() == "vista":
        return "Accent.TButton"
    return "TButton"

# Sets up the main window, initializes styles, constructs all UI components, and binds event handlers for the application.
def initialize_gui() -> None:
    root = tk.Tk()
    root.title(f"{TITLE} — {SUBTITLE}")
    root.minsize(560, 300)
    root.geometry("640x340")

    style = _setup_style(root)

    main = ttk.Frame(root, style="App.TFrame", padding=(24, 20))
    main.pack(fill=tk.BOTH, expand=True)

    head = ttk.Frame(main, style="App.TFrame")
    head.pack(fill=tk.X, pady=(0, 4))
    ttk.Label(head, text=TITLE, style="Title.TLabel").pack(anchor="w")
    ttk.Label(head, text=SUBTITLE, style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

    ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(14, 16))

    entry_var = tk.StringVar()
    entry = ttk.Entry(main, textvariable=entry_var, width=72)
    entry.pack(fill=tk.X, pady=(0, 14))
    entry.focus_set()

    btn_row = ttk.Frame(main, style="App.TFrame")
    btn_row.pack(fill=tk.X, pady=(0, 16))

    status_var = tk.StringVar(value=_DEFAULT_STATUS)

    # Status card: flat border + slim left accent (tk for precise colors)
    card = tk.Frame(main, bg=_CARD, highlightbackground=_CARD_BORDER, highlightthickness=1)
    card.pack(fill=tk.BOTH, expand=True)
    inner = tk.Frame(card, bg=_CARD)
    inner.pack(fill=tk.BOTH, expand=True)

    accent_strip = tk.Frame(inner, width=4, bg=_STRIP_NEUTRAL, highlightthickness=0)
    accent_strip.pack(side=tk.LEFT, fill=tk.Y)

    text_host = tk.Frame(inner, bg=_CARD)
    text_host.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 16), pady=(14, 14))

    body_font = tkfont.Font(family="Segoe UI", size=10)
    status_lbl = tk.Label(
        text_host,
        textvariable=status_var,
        bg=_CARD,
        fg=_TEXT,
        font=body_font,
        wraplength=520,
        justify=tk.LEFT,
        anchor="w",
    )
    status_lbl.pack(fill=tk.BOTH, expand=True)

    # Dynamically updates the text wrapping width of the status label when the window is resized.
    def _sync_wrap(_event: tk.Event | None = None) -> None:
        try:
            w = max(text_host.winfo_width() - 8, 240)
            status_lbl.configure(wraplength=w)
        except tk.TclError:
            pass

    text_host.bind("<Configure>", _sync_wrap)

    # Updates the background color of the accent strip on the status card.
    def set_accent(color: str) -> None:
        accent_strip.configure(bg=color)

    # Updates the UI with appropriate colors and messages based on the evaluated credibility status (FAKE, UGC, UNKNOWN).
    def apply_credibility_style(status: str) -> None:
        if status == "FAKE":
            set_accent(_STRIP_FAKE)
            status_var.set(
                "FAKE — this host matches your local blocklist of known unreliable domains."
            )
        elif status == "UGC":
            set_accent(_STRIP_UGC)
            status_var.set(
                "UGC — neutral hosting platform; treat posts as user-generated and verify elsewhere."
            )
        else:
            set_accent(_STRIP_UNKNOWN)
            status_var.set(
                "UNKNOWN — no list match. Opening a targeted fact-check search in your browser."
            )

    # Displays an error message in the status card and changes the accent strip to the error color.
    def show_gui_error(message: str) -> None:
        set_accent(_STRIP_ERROR)
        status_var.set(f"Error: {message}")

    # Attempts to load datasets on startup and updates the status UI to show warnings if any files are missing.
    def apply_startup_warning() -> None:
        load_datasets()
        if last_load_error:
            set_accent(_STRIP_ERROR)
            status_var.set(
                f"Warning: {last_load_error} (empty sets used where files are missing)."
            )
        else:
            set_accent(_STRIP_NEUTRAL)
            status_var.set(_DEFAULT_STATUS)

    # Handles the submit action: evaluates input credibility, updates the UI, executes the search, and logs the query.
    def on_submit(_event=None) -> None:
        raw = entry_var.get()
        if not raw.strip():
            show_gui_error("Please enter a URL or a short statement.")
            return
        try:
            input_type, parsed = process_input(raw)
            status = evaluate_credibility(input_type, parsed)
            apply_credibility_style(status)
            root.update_idletasks()

            user_query = sanitize_for_log(raw.strip())
            log_err = execute_search(user_query)
            if log_err:
                status_var.set(status_var.get() + "\n\n" + log_err)
        except OSError as exc:
            show_gui_error(str(exc))
        except Exception as exc:  # noqa: BLE001
            show_gui_error(str(exc))

    # Resets the input field and status card to their default neutral states.
    def on_clear() -> None:
        entry_var.set("")
        set_accent(_STRIP_NEUTRAL)
        status_var.set(_DEFAULT_STATUS)

    # Opens a dialog to flag a new source, updates the blocklist, and provides feedback in the status area.
    def on_flag() -> None:
        ok, _ = flag_new_source(root)
        if ok:
            if last_load_error:
                set_accent(_STRIP_ERROR)
                status_var.set(f"Domain saved. Note: {last_load_error}")
            else:
                set_accent(_STRIP_NEUTRAL)
                status_var.set(_DEFAULT_STATUS + " Blocklist reloaded.")

    submit_btn = ttk.Button(
        btn_row,
        text="Submit",
        style=_submit_button_style(style),
        command=on_submit,
    )
    submit_btn.pack(side=tk.LEFT, padx=(0, 8))

    ttk.Button(btn_row, text="Clear", style="Ghost.TButton", command=on_clear).pack(
        side=tk.LEFT, padx=(0, 8)
    )
    ttk.Button(btn_row, text="Flag source…", style="Ghost.TButton", command=on_flag).pack(
        side=tk.LEFT
    )

    entry.bind("<Return>", on_submit)

    apply_startup_warning()
    root.mainloop()

if __name__ == "__main__":
    initialize_gui()