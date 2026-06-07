import tkinter as tk
from tkinter import ttk

# ─── COLOR PALETTE ──────────────────────────────────────────────────
NAVY       = "#0B1F3A"
NAVY_LIGHT = "#132D54"
BLUE       = "#1A6FC4"
CYAN       = "#00C9A7"
CYAN_DARK  = "#00A589"
WHITE      = "#FFFFFF"
OFF_WHITE  = "#F0F5FB"
GRAY_LIGHT = "#E2EAF4"
GRAY       = "#8FA3BC"
DARK_TEXT  = "#0B1F3A"
GOLD       = "#F5A623"
RED        = "#E84141"
GREEN      = "#27AE60"
PURPLE     = "#7B2FBE"
ORANGE     = "#E67E22"

# ─── FONTS ──────────────────────────────────────────────────────────
FONT_HERO    = ("Georgia", 42, "bold")
FONT_TITLE   = ("Georgia", 22, "bold")
FONT_HEADING = ("Helvetica", 16, "bold")
FONT_SUB     = ("Helvetica", 12, "bold")
FONT_BODY    = ("Helvetica", 11)
FONT_SMALL   = ("Helvetica", 9)
FONT_BTN     = ("Helvetica", 11, "bold")
FONT_TAG     = ("Helvetica", 10, "bold")

def configure_styles():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame", background=OFF_WHITE)
    style.configure("Navy.TFrame", background=NAVY)
    style.configure("White.TFrame", background=WHITE)
    style.configure("Card.TFrame", background=WHITE, relief="flat")

    style.configure("TLabel", background=OFF_WHITE, foreground=DARK_TEXT, font=FONT_BODY)
    style.configure("White.TLabel", background=WHITE, foreground=DARK_TEXT, font=FONT_BODY)
    style.configure("Navy.TLabel", background=NAVY, foreground=WHITE, font=FONT_BODY)
    style.configure("Heading.TLabel", background=WHITE, foreground=DARK_TEXT, font=FONT_HEADING)
    style.configure("Sub.TLabel", background=WHITE, foreground=GRAY, font=FONT_SMALL)
    style.configure("NavyHeading.TLabel", background=NAVY, foreground=CYAN, font=FONT_HEADING)

    style.configure("TEntry",
        fieldbackground=WHITE, foreground=DARK_TEXT,
        font=FONT_BODY, padding=8, relief="flat"
    )
    
    # FIX: Enhanced TCombobox styling for dynamic forms
    style.configure("TCombobox",
        fieldbackground=WHITE, foreground=DARK_TEXT,
        font=FONT_BODY, padding=6, arrowsize=14
    )
    style.map("TCombobox", 
        fieldbackground=[("readonly", WHITE)],
        selectbackground=[("readonly", WHITE)],
        selectforeground=[("readonly", DARK_TEXT)]
    )

    style.configure("Primary.TButton",
        background=BLUE, foreground=WHITE,
        font=FONT_BTN, padding=(20, 10), relief="flat", borderwidth=0
    )
    style.map("Primary.TButton",
        background=[("active", "#145EA0"), ("pressed", "#0F4B82")],
        foreground=[("active", WHITE)]
    )

    style.configure("Cyan.TButton",
        background=CYAN, foreground=WHITE,
        font=FONT_BTN, padding=(20, 10), relief="flat", borderwidth=0
    )
    style.map("Cyan.TButton",
        background=[("active", CYAN_DARK), ("pressed", "#008A6F")],
    )

    style.configure("Danger.TButton",
        background=RED, foreground=WHITE,
        font=FONT_BTN, padding=(16, 8), relief="flat", borderwidth=0
    )
    style.map("Danger.TButton", background=[("active", "#C0392B")])

    style.configure("Success.TButton",
        background=GREEN, foreground=WHITE,
        font=FONT_BTN, padding=(16, 8), relief="flat", borderwidth=0
    )
    style.map("Success.TButton", background=[("active", "#1E8449")])

    style.configure("Gold.TButton",
        background=GOLD, foreground=WHITE,
        font=FONT_BTN, padding=(16, 8), relief="flat", borderwidth=0
    )
    style.map("Gold.TButton", background=[("active", "#D4891E")])

    style.configure("Ghost.TButton",
        background=NAVY_LIGHT, foreground=WHITE,
        font=FONT_BTN, padding=(20, 10), relief="flat", borderwidth=0
    )
    style.map("Ghost.TButton", background=[("active", NAVY)])

    style.configure("Treeview",
        background=WHITE, foreground=DARK_TEXT,
        rowheight=32, font=FONT_BODY, fieldbackground=WHITE
    )
    style.configure("Treeview.Heading",
        background=NAVY, foreground=WHITE,
        font=FONT_SUB, relief="flat", padding=(5, 8)
    )
    style.map("Treeview",
        background=[("selected", BLUE)],
        foreground=[("selected", WHITE)]
    )

    style.configure("TNotebook", background=OFF_WHITE, tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab",
        background=GRAY_LIGHT, foreground=DARK_TEXT,
        font=FONT_SUB, padding=(16, 8)
    )
    style.map("TNotebook.Tab",
        background=[("selected", NAVY)],
        foreground=[("selected", WHITE)]
    )

    return style


def make_card(parent, bg=WHITE, padx=20, pady=20):
    """Create a card-style frame with shadow-like border."""
    outer = tk.Frame(parent, bg=GRAY_LIGHT, padx=1, pady=1)
    inner = tk.Frame(outer, bg=bg, padx=padx, pady=pady)
    inner.pack(fill="both", expand=True)
    return outer, inner


def make_label(parent, text, font=FONT_BODY, fg=DARK_TEXT, bg=WHITE, **kw):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)


def make_entry(parent, width=28, show=None):
    e = tk.Entry(parent, width=width, font=FONT_BODY, fg=DARK_TEXT,
                 bg=WHITE, relief="solid", bd=1,
                 highlightthickness=2, highlightcolor=CYAN,
                 highlightbackground=GRAY_LIGHT)
    if show:
        e.config(show=show)
    return e


def make_button(parent, text, command, color=BLUE, pady=8, padx=15):
    # We use a flat relief and specific cursor to make it feel like a modern UI
    btn = tk.Button(
        parent, 
        text=text, 
        command=command,
        bg=color, 
        fg=WHITE,
        font=FONT_BTN,
        relief="flat",
        activebackground=NAVY,
        activeforeground=WHITE,
        cursor="hand2", # Changes cursor to a hand when hovering
        pady=pady,
        padx=padx
    )
    return btn


def darken(hex_color):
    """Return a slightly darker version of a hex color."""
    try:
        r = max(0, int(hex_color[1:3], 16) - 25)
        g = max(0, int(hex_color[3:5], 16) - 25)
        b = max(0, int(hex_color[5:7], 16) - 25)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


def scrollable_frame(parent, bg=OFF_WHITE):
    """Returns (outer_frame, canvas, inner_frame) for a scrollable area."""
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)

    # FIX: Added dynamic width synchronization so inner frame expands with canvas
    def _on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", _on_canvas_configure)
    
    canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # FIX: Bind mousewheel to all elements to ensure scrolling works everywhere
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return outer, canvas, inner


def section_header(parent, text, bg=OFF_WHITE, fg=NAVY):
    frame = tk.Frame(parent, bg=bg)
    tk.Label(frame, text=text, font=FONT_HEADING, fg=fg, bg=bg).pack(side="left", pady=(0, 12))
    tk.Frame(frame, bg=CYAN, height=3).pack(side="bottom", fill="x")
    return frame


def stat_card(parent, label, value, color=BLUE, bg=WHITE):
    f = tk.Frame(parent, bg=color, padx=24, pady=18)
    tk.Label(f, text=str(value), font=("Helvetica", 26, "bold"), fg=WHITE, bg=color).pack()
    tk.Label(f, text=label, font=FONT_SMALL, fg=WHITE, bg=color).pack()
    return f


def tag_label(parent, text, color=CYAN):
    return tk.Label(parent, text=f"  {text}  ", bg=color, fg=WHITE,
                    font=FONT_TAG, padx=4, pady=2, relief="flat")