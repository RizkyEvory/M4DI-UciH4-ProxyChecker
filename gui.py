#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
           ███╗   ███╗██╗  ██╗██████╗ ██╗    ██╗   ██╗ ██████╗██╗██╗  ██╗██╗  ██╗
           ████╗ ████║██║  ██║██╔══██╗██║    ██║   ██║██╔════╝██║██║  ██║██║  ██║
           ██╔████╔██║███████║██║  ██║██║    ██║   ██║██║     ██║███████║███████║
           ██║╚██╔╝██║╚════██║██║  ██║██║    ██║   ██║██║     ██║██╔══██║╚════██║
           ██║ ╚═╝ ██║     ██║██████╔╝██║    ╚██████╔╝╚██████╗██║██║  ██║     ██║
           ╚═╝     ╚═╝     ╚═╝╚═════╝ ╚═╝     ╚═════╝  ╚═════╝╚═╝╚═╝  ╚═╝     ╚═╝
========================================================================================
            ⚡ M 4 D I ~ U c i H 4  P R O X Y  C H E C K E R  G U I  E L I T E ⚡
                     [ CYBER SHARINGAN TKINTER AUDITOR v4.0 ]
========================================================================================
 Coded with Passion by: M4DI~UciH4
 Graphical User Interface (Built-in Tkinter)
 Zero external GUI dependencies. High speed, responsive, multi-threaded & bug-free.
========================================================================================
"""

import sys
import os
import time
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional, Dict, Any

# Ensure script directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import backend modules
try:
    from checker import (
        ProxyParser, ProxyCheckerEngine, ProxyItem, CheckResult,
        ResultsManager, GeoIPResolver
    )
except ImportError as e:
    messagebox.showerror("Dependency Error", f"Failed to import core checker engine:\n{e}")
    sys.exit(1)

try:
    import scraper
    HAVE_SCRAPER = True
except ImportError:
    HAVE_SCRAPER = False


# ============================================================================
# MODERN CYBER DARK PALETTE (UCHIHA / SHARINGAN THEME)
# ============================================================================
THEME = {
    "bg_main": "#0b0d13",          # Deep midnight obsidian
    "bg_card": "#131722",          # Elevated panel background
    "bg_card_alt": "#1a202e",      # Input / item background
    "border": "#252d3d",           # Border lines
    "accent_red": "#ff2a44",       # Sharingan crimson neon
    "accent_red_hover": "#e01e38", # Darker crimson
    "accent_cyan": "#00f0ff",      # Electric neon cyan
    "accent_green": "#00e676",     # Vivid matrix alive green
    "accent_yellow": "#ffd166",    # Warm gold SOCKS4
    "accent_blue": "#38bdf8",      # HTTP neon blue
    "text_primary": "#f8fafc",     # Bright white text
    "text_secondary": "#94a3b8",   # Muted subtext
    "text_dim": "#64748b",         # Disabled / placeholder
    "dead_color": "#ef4444"        # Dead red
}


class M4DIUciH4ProxyGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("⚡ M4DI~UciH4 PROXY CHECKER ELITE v4.0 ⚡ [CYBER SHARINGAN ENGINE]")
        self.root.geometry("1180x760")
        self.root.minsize(980, 620)
        self.root.configure(bg=THEME["bg_main"])

        # Threading & Communication
        self.msg_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread: Optional[threading.Thread] = None
        self.is_running = False

        # State & Counters
        self.proxies_loaded: List[ProxyItem] = []
        self.alive_results: List[CheckResult] = []
        self.total_count = 0
        self.checked_count = 0
        self.alive_count = 0
        self.dead_count = 0
        self.socks5_count = 0
        self.socks4_count = 0
        self.http_count = 0
        self.start_time = 0.0

        # Engine & Persistence
        self.engine: Optional[ProxyCheckerEngine] = None
        self.res_manager: Optional[ResultsManager] = None
        self.filter_alive_only = tk.BooleanVar(value=False)

        # Build UI
        self._setup_styles()
        self._build_header()
        self._build_controls()
        self._build_metric_cards()
        self._build_tabs_and_table()
        self._build_status_bar()

        # Start Queue Poller
        self.root.after(40, self._process_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Auto-load proxies.txt if exists
        default_proxies = os.path.join(SCRIPT_DIR, "proxies.txt")
        if os.path.exists(default_proxies):
            self._load_file(default_proxies)

    # ------------------------------------------------------------------------
    # TTK STYLING
    # ------------------------------------------------------------------------
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Configure generic TTK colors
        style.configure(".", background=THEME["bg_card"], foreground=THEME["text_primary"],
                        bordercolor=THEME["border"], font=("Segoe UI", 9))

        # Treeview (The live table)
        style.configure(
            "Custom.Treeview",
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            fieldbackground=THEME["bg_card"],
            rowheight=26,
            font=("Consolas", 9),
            bordercolor=THEME["border"]
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", THEME["bg_card_alt"])],
            foreground=[("selected", THEME["accent_cyan"])]
        )

        style.configure(
            "Custom.Treeview.Heading",
            background=THEME["bg_card_alt"],
            foreground=THEME["accent_cyan"],
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padding=5
        )
        style.map("Custom.Treeview.Heading", background=[("active", THEME["border"])])

        # Progressbar
        style.configure(
            "Crimson.Horizontal.TProgressbar",
            troughcolor=THEME["bg_card_alt"],
            background=THEME["accent_red"],
            bordercolor=THEME["border"],
            lightcolor=THEME["accent_red"],
            darkcolor=THEME["accent_red"]
        )

        # Notebook tabs
        style.configure(
            "TNotebook",
            background=THEME["bg_main"],
            bordercolor=THEME["border"]
        )
        style.configure(
            "TNotebook.Tab",
            background=THEME["bg_card"],
            foreground=THEME["text_secondary"],
            padding=[16, 6],
            font=("Segoe UI", 9, "bold")
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", THEME["bg_card_alt"])],
            foreground=[("selected", THEME["accent_red"])]
        )

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=THEME["bg_card_alt"],
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            arrowcolor=THEME["accent_cyan"],
            bordercolor=THEME["border"]
        )

    # ------------------------------------------------------------------------
    # HEADER BANNER
    # ------------------------------------------------------------------------
    def _build_header(self):
        header_frame = tk.Frame(self.root, bg=THEME["bg_card"], height=65, highlightthickness=1,
                                highlightbackground=THEME["border"])
        header_frame.pack(fill=tk.X, side=tk.TOP, padx=12, pady=(10, 6))

        # Title block
        title_box = tk.Frame(header_frame, bg=THEME["bg_card"])
        title_box.pack(side=tk.LEFT, padx=16, pady=8)

        lbl_title = tk.Label(
            title_box,
            text="⚡ M4DI~UciH4 PROXY CHECKER ELITE",
            font=("Segoe UI", 15, "bold"),
            fg=THEME["accent_red"],
            bg=THEME["bg_card"]
        )
        lbl_title.pack(anchor="w")

        lbl_subtitle = tk.Label(
            title_box,
            text="CYBER SHARINGAN MULTI-PROTOCOL AUDITOR v4.0  //  [HTTP • HTTPS • SOCKS4 • SOCKS5]",
            font=("Segoe UI", 8),
            fg=THEME["accent_cyan"],
            bg=THEME["bg_card"]
        )
        lbl_subtitle.pack(anchor="w")

        # Right branding badge
        badge_box = tk.Frame(header_frame, bg=THEME["bg_card"])
        badge_box.pack(side=tk.RIGHT, padx=16, pady=10)

        lbl_dev = tk.Label(
            badge_box,
            text="CODED BY: M4DI~UciH4",
            font=("Segoe UI", 10, "bold"),
            fg="#ffffff",
            bg=THEME["accent_red"],
            padx=10,
            pady=3
        )
        lbl_dev.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------------
    # CONTROLS PANEL
    # ------------------------------------------------------------------------
    def _build_controls(self):
        ctrl_frame = tk.Frame(self.root, bg=THEME["bg_card"], highlightthickness=1,
                              highlightbackground=THEME["border"])
        ctrl_frame.pack(fill=tk.X, padx=12, pady=4)

        # Row 1: File selection and quick inputs
        row1 = tk.Frame(ctrl_frame, bg=THEME["bg_card"])
        row1.pack(fill=tk.X, padx=12, pady=(8, 6))

        tk.Label(row1, text="Proxy List File:", font=("Segoe UI", 9, "bold"),
                 fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))

        self.file_entry_var = tk.StringVar(value=os.path.join(SCRIPT_DIR, "proxies.txt"))
        self.entry_file = tk.Entry(
            row1,
            textvariable=self.file_entry_var,
            font=("Segoe UI", 9),
            bg=THEME["bg_card_alt"],
            fg=THEME["text_primary"],
            insertbackground=THEME["text_primary"],
            relief="flat",
            width=45,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.entry_file.pack(side=tk.LEFT, padx=(0, 8), ipady=3)

        btn_browse = tk.Button(
            row1,
            text="📂 Browse File",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card_alt"],
            fg=THEME["text_primary"],
            activebackground=THEME["border"],
            activeforeground=THEME["text_primary"],
            relief="flat",
            padx=10,
            pady=2,
            command=self._on_browse_file,
            cursor="hand2"
        )
        btn_browse.pack(side=tk.LEFT, padx=(0, 14))

        # Quick single proxy entry
        tk.Label(row1, text="Quick Single IP:Port:", font=("Segoe UI", 9, "bold"),
                 fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))

        self.quick_proxy_var = tk.StringVar()
        self.entry_quick = tk.Entry(
            row1,
            textvariable=self.quick_proxy_var,
            font=("Consolas", 9),
            bg=THEME["bg_card_alt"],
            fg=THEME["text_primary"],
            insertbackground=THEME["text_primary"],
            relief="flat",
            width=22,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.entry_quick.pack(side=tk.LEFT, padx=(0, 8), ipady=3)

        btn_add_quick = tk.Button(
            row1,
            text="➕ Check Single",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card_alt"],
            fg=THEME["accent_cyan"],
            activebackground=THEME["border"],
            relief="flat",
            padx=8,
            pady=2,
            command=self._on_check_single,
            cursor="hand2"
        )
        btn_add_quick.pack(side=tk.LEFT)

        # Row 2: Parameters & Action Buttons
        row2 = tk.Frame(ctrl_frame, bg=THEME["bg_card"])
        row2.pack(fill=tk.X, padx=12, pady=(0, 10))

        # Protocol Mode Combobox
        tk.Label(row2, text="Protocol:", font=("Segoe UI", 9, "bold"),
                 fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))

        self.proto_mode_var = tk.StringVar(value="Auto-Detect (Smart Probe)")
        combo_proto = ttk.Combobox(
            row2,
            textvariable=self.proto_mode_var,
            values=["Auto-Detect (Smart Probe)", "SOCKS5 Only", "SOCKS4 Only", "HTTP / HTTPS Only"],
            state="readonly",
            width=23
        )
        combo_proto.pack(side=tk.LEFT, padx=(0, 14))

        # Threads Spinbox
        tk.Label(row2, text="Threads:", font=("Segoe UI", 9, "bold"),
                 fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(side=tk.LEFT, padx=(0, 4))
        self.threads_var = tk.IntVar(value=50)
        sp_threads = tk.Spinbox(
            row2,
            from_=1, to=200,
            textvariable=self.threads_var,
            width=4,
            bg=THEME["bg_card_alt"],
            fg=THEME["text_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        sp_threads.pack(side=tk.LEFT, padx=(0, 14))

        # Timeout Spinbox
        tk.Label(row2, text="Timeout (s):", font=("Segoe UI", 9, "bold"),
                 fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(side=tk.LEFT, padx=(0, 4))
        self.timeout_var = tk.IntVar(value=5)
        sp_timeout = tk.Spinbox(
            row2,
            from_=2, to=20,
            textvariable=self.timeout_var,
            width=4,
            bg=THEME["bg_card_alt"],
            fg=THEME["text_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        sp_timeout.pack(side=tk.LEFT, padx=(0, 14))

        # Pre-ping Checkbox
        self.preping_var = tk.BooleanVar(value=True)
        chk_ping = tk.Checkbutton(
            row2,
            text="⚡ Fast TCP Ping",
            variable=self.preping_var,
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            selectcolor=THEME["bg_card_alt"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["accent_cyan"],
            font=("Segoe UI", 9)
        )
        chk_ping.pack(side=tk.LEFT, padx=(0, 14))

        # ACTION BUTTONS (Right-aligned)
        self.btn_start = tk.Button(
            row2,
            text="▶ START SCAN",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["accent_red"],
            fg="#ffffff",
            activebackground=THEME["accent_red_hover"],
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=3,
            cursor="hand2",
            command=self._on_start_scan
        )
        self.btn_start.pack(side=tk.RIGHT, padx=4)

        self.btn_stop = tk.Button(
            row2,
            text="⏹ STOP",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card_alt"],
            fg=THEME["dead_color"],
            activebackground=THEME["border"],
            relief="flat",
            padx=12,
            pady=3,
            state="disabled",
            cursor="hand2",
            command=self._on_stop_scan
        )
        self.btn_stop.pack(side=tk.RIGHT, padx=4)

        btn_scrape = tk.Button(
            row2,
            text="🌐 AUTO-HARVEST",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card_alt"],
            fg=THEME["accent_cyan"],
            activebackground=THEME["border"],
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._on_auto_harvest
        )
        btn_scrape.pack(side=tk.RIGHT, padx=4)

        btn_clear = tk.Button(
            row2,
            text="🗑 Clear",
            font=("Segoe UI", 9),
            bg=THEME["bg_card_alt"],
            fg=THEME["text_secondary"],
            activebackground=THEME["border"],
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._on_clear_results
        )
        btn_clear.pack(side=tk.RIGHT, padx=4)

    # ------------------------------------------------------------------------
    # METRIC COUNTER CARDS
    # ------------------------------------------------------------------------
    def _build_metric_cards(self):
        metrics_container = tk.Frame(self.root, bg=THEME["bg_main"])
        metrics_container.pack(fill=tk.X, padx=12, pady=4)

        self.card_labels: Dict[str, tk.Label] = {}

        card_defs = [
            ("TOTAL", "0", THEME["text_primary"]),
            ("ALIVE", "0", THEME["accent_green"]),
            ("DEAD", "0", THEME["dead_color"]),
            ("SOCKS5", "0", THEME["accent_cyan"]),
            ("SOCKS4", "0", THEME["accent_yellow"]),
            ("HTTP", "0", THEME["accent_blue"]),
            ("TIME", "00:00", THEME["text_secondary"])
        ]

        for title, default_val, color in card_defs:
            card = tk.Frame(metrics_container, bg=THEME["bg_card"], highlightthickness=1,
                            highlightbackground=THEME["border"])
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=3, pady=2)

            lbl_val = tk.Label(card, text=default_val, font=("Consolas", 14, "bold"),
                               fg=color, bg=THEME["bg_card"])
            lbl_val.pack(anchor="center", pady=(5, 0))

            lbl_title = tk.Label(card, text=title, font=("Segoe UI", 7, "bold"),
                                 fg=THEME["text_dim"], bg=THEME["bg_card"])
            lbl_title.pack(anchor="center", pady=(0, 4))

            self.card_labels[title] = lbl_val

        # Progress bar under cards
        prog_frame = tk.Frame(self.root, bg=THEME["bg_main"])
        prog_frame.pack(fill=tk.X, padx=12, pady=(4, 2))

        self.progress_bar = ttk.Progressbar(
            prog_frame,
            orient="horizontal",
            mode="determinate",
            style="Crimson.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=1)

        self.lbl_progress_pct = tk.Label(
            prog_frame,
            text="0% (0/0)",
            font=("Segoe UI", 8, "bold"),
            fg=THEME["text_secondary"],
            bg=THEME["bg_main"],
            padx=8
        )
        self.lbl_progress_pct.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------------
    # TABS & DATA TABLE
    # ------------------------------------------------------------------------
    def _build_tabs_and_table(self):
        tab_container = tk.Frame(self.root, bg=THEME["bg_main"])
        tab_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        self.notebook = ttk.Notebook(tab_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Proxy Grid View
        frame_grid = tk.Frame(self.notebook, bg=THEME["bg_card"])
        self.notebook.add(frame_grid, text="📊 Live Proxy Grid")

        # Table Control Sub-bar
        tbl_ctrl = tk.Frame(frame_grid, bg=THEME["bg_card"])
        tbl_ctrl.pack(fill=tk.X, padx=8, pady=4)

        chk_filter = tk.Checkbutton(
            tbl_ctrl,
            text="Show Alive Only",
            variable=self.filter_alive_only,
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            selectcolor=THEME["bg_card_alt"],
            activebackground=THEME["bg_card"],
            font=("Segoe UI", 9),
            command=self._refresh_table_view
        )
        chk_filter.pack(side=tk.LEFT)

        btn_export = tk.Button(
            tbl_ctrl,
            text="💾 Export Results (TXT/JSON/CSV)",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["bg_card_alt"],
            fg=THEME["accent_green"],
            activebackground=THEME["border"],
            relief="flat",
            padx=8,
            pady=1,
            command=self._on_export_dialog,
            cursor="hand2"
        )
        btn_export.pack(side=tk.RIGHT)

        btn_copy_all = tk.Button(
            tbl_ctrl,
            text="📋 Copy All Alive",
            font=("Segoe UI", 8),
            bg=THEME["bg_card_alt"],
            fg=THEME["text_primary"],
            activebackground=THEME["border"],
            relief="flat",
            padx=8,
            pady=1,
            command=self._copy_all_alive,
            cursor="hand2"
        )
        btn_copy_all.pack(side=tk.RIGHT, padx=4)

        # Table Frame with Scrollbars
        tree_frame = tk.Frame(frame_grid, bg=THEME["bg_card"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        columns = ("no", "proxy", "proto", "status", "speed", "anonymity", "ssl", "country", "isp")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="extended"
        )

        col_config = [
            ("no", "#", 45, "center"),
            ("proxy", "Proxy Address", 190, "w"),
            ("proto", "Protocol", 75, "center"),
            ("status", "Status", 75, "center"),
            ("speed", "Speed", 75, "center"),
            ("anonymity", "Anonymity", 100, "center"),
            ("ssl", "SSL", 55, "center"),
            ("country", "Country", 150, "w"),
            ("isp", "ISP / Organization", 250, "w")
        ]

        for col_id, col_name, col_width, col_anchor in col_config:
            self.tree.heading(col_id, text=col_name)
            self.tree.column(col_id, width=col_width, anchor=col_anchor, stretch=True)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Row color tags
        self.tree.tag_configure("alive_elite", foreground=THEME["accent_green"])
        self.tree.tag_configure("alive_anon", foreground=THEME["accent_cyan"])
        self.tree.tag_configure("alive_trans", foreground=THEME["accent_yellow"])
        self.tree.tag_configure("dead", foreground=THEME["text_dim"])

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=THEME["bg_card_alt"], fg=THEME["text_primary"],
                                    activebackground=THEME["accent_red"], activeforeground="#ffffff")
        self.context_menu.add_command(label="Copy Proxy (IP:Port)", command=self._copy_selected_proxy)
        self.context_menu.add_command(label="Copy Full URL (protocol://ip:port)", command=self._copy_selected_url)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Entire Row", command=self._copy_selected_row)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self._copy_selected_url())

        # Tab 2: Raw Paste Input Area
        frame_paste = tk.Frame(self.notebook, bg=THEME["bg_card"])
        self.notebook.add(frame_paste, text="📝 Paste Proxies Directly")

        tk.Label(
            frame_paste,
            text="Paste your proxy list below (Format: 185.80.196.126:3128 or socks5://...):",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["accent_cyan"],
            bg=THEME["bg_card"]
        ).pack(anchor="w", padx=12, pady=(10, 4))

        self.txt_paste = tk.Text(
            frame_paste,
            bg=THEME["bg_card_alt"],
            fg=THEME["text_primary"],
            insertbackground=THEME["text_primary"],
            relief="flat",
            font=("Consolas", 9),
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.txt_paste.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        btn_load_pasted = tk.Button(
            frame_paste,
            text="📥 Load Pasted Proxies to Queue",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["accent_red"],
            fg="#ffffff",
            activebackground=THEME["accent_red_hover"],
            relief="flat",
            padx=14,
            pady=4,
            command=self._on_load_pasted,
            cursor="hand2"
        )
        btn_load_pasted.pack(anchor="e", padx=12, pady=(0, 10))

        # Tab 3: Console Live Log
        frame_log = tk.Frame(self.notebook, bg=THEME["bg_card"])
        self.notebook.add(frame_log, text="📜 Activity Log")

        self.txt_log = tk.Text(
            frame_log,
            bg=THEME["bg_card_alt"],
            fg=THEME["text_secondary"],
            font=("Consolas", 9),
            relief="flat",
            state="disabled",
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

    # ------------------------------------------------------------------------
    # STATUS BAR
    # ------------------------------------------------------------------------
    def _build_status_bar(self):
        status_frame = tk.Frame(self.root, bg=THEME["bg_card"], height=26, highlightthickness=1,
                                highlightbackground=THEME["border"])
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status = tk.Label(
            status_frame,
            text="Ready. System armed. Results will be saved to results.txt",
            font=("Segoe UI", 8),
            fg=THEME["text_secondary"],
            bg=THEME["bg_card"],
            padx=10
        )
        self.lbl_status.pack(side=tk.LEFT)

        self.lbl_ip_baseline = tk.Label(
            status_frame,
            text="Detecting Real IP Baseline...",
            font=("Segoe UI", 8, "bold"),
            fg=THEME["accent_cyan"],
            bg=THEME["bg_card"],
            padx=10
        )
        self.lbl_ip_baseline.pack(side=tk.RIGHT)

        # Query baseline IP in background
        threading.Thread(target=self._async_fetch_baseline_ip, daemon=True).start()

    def _async_fetch_baseline_ip(self):
        try:
            engine = ProxyCheckerEngine(timeout=3, pre_ping=False)
            ip = engine.my_real_ip
            self.msg_queue.put(("BASELINE_IP", ip))
        except Exception:
            pass

    # ------------------------------------------------------------------------
    # EVENT HANDLERS & ACTIONS
    # ------------------------------------------------------------------------
    def _on_browse_file(self):
        path = filedialog.askopenfilename(
            title="Select Proxy List",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir=SCRIPT_DIR
        )
        if path:
            self.file_entry_var.set(path)
            self._load_file(path)

    def _load_file(self, filepath: str):
        if not os.path.exists(filepath):
            return
        parsed: List[ProxyItem] = []
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    item = ProxyParser.parse_line(line)
                    if item:
                        parsed.append(item)
            self.proxies_loaded = parsed
            self.card_labels["TOTAL"].config(text=str(len(parsed)))
            self._log(f"[+] Loaded {len(parsed)} proxies from '{os.path.basename(filepath)}'")
            self.lbl_status.config(text=f"Loaded {len(parsed)} proxies ready to audit.")
        except Exception as e:
            messagebox.showerror("File Error", f"Failed to load file: {e}")

    def _on_load_pasted(self):
        text = self.txt_paste.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty Input", "Please paste proxy entries first.")
            return

        parsed: List[ProxyItem] = []
        for line in text.splitlines():
            item = ProxyParser.parse_line(line)
            if item:
                parsed.append(item)

        if not parsed:
            messagebox.showwarning("Parse Error", "No valid IP:Port formats found in pasted text.")
            return

        self.proxies_loaded = parsed
        self.card_labels["TOTAL"].config(text=str(len(parsed)))
        self._log(f"[+] Loaded {len(parsed)} proxies from manual paste area.")
        self.notebook.select(0)  # Switch back to table tab
        messagebox.showinfo("Proxies Loaded", f"Successfully loaded {len(parsed)} proxies into queue!")

    def _on_check_single(self):
        raw = self.quick_proxy_var.get().strip()
        if not raw:
            messagebox.showwarning("Input Required", "Please enter a proxy (e.g. 167.99.3.26:9050)")
            return
        item = ProxyParser.parse_line(raw)
        if not item:
            messagebox.showerror("Invalid Format", "Invalid proxy syntax. Supported: IP:PORT or socks5://IP:PORT")
            return

        self.proxies_loaded = [item]
        self._on_start_scan()

    def _on_auto_harvest(self):
        if not HAVE_SCRAPER:
            messagebox.showerror("Error", "scraper.py module not found in script directory.")
            return

        self._log("[*] Harvesting live public proxies from multiple high-uptime endpoints...")
        self.lbl_status.config(text="Scraping public proxies in background...")

        def harvest_job():
            try:
                data = scraper.scrape_proxies("all")
                combined = data.get("socks5", []) + data.get("socks4", []) + data.get("http", [])
                parsed = []
                for p in combined:
                    it = ProxyParser.parse_line(p)
                    if it:
                        parsed.append(it)
                self.msg_queue.put(("HARVEST_DONE", parsed))
            except Exception as e:
                self.msg_queue.put(("LOG", f"[!] Harvest error: {e}"))

        threading.Thread(target=harvest_job, daemon=True).start()

    def _on_start_scan(self):
        if self.is_running:
            return

        if not self.proxies_loaded:
            # Try reloading from file entry
            fpath = self.file_entry_var.get().strip()
            if os.path.exists(fpath):
                self._load_file(fpath)

        if not self.proxies_loaded:
            messagebox.showwarning("No Proxies", "No proxies loaded. Please select a file, paste proxies, or click AUTO-HARVEST.")
            return

        # Read parameters
        mode_str = self.proto_mode_var.get()
        if "SOCKS5" in mode_str:
            mode = "socks5"
        elif "SOCKS4" in mode_str:
            mode = "socks4"
        elif "HTTP" in mode_str:
            mode = "http"
        else:
            mode = "auto"

        threads = max(1, min(200, self.threads_var.get()))
        timeout = max(2, min(20, self.timeout_var.get()))
        pre_ping = self.preping_var.get()

        # Reset states
        self.is_running = True
        self.stop_event.clear()
        self.checked_count = 0
        self.alive_count = 0
        self.dead_count = 0
        self.socks5_count = 0
        self.socks4_count = 0
        self.http_count = 0
        self.alive_results.clear()
        self.start_time = time.time()

        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.tree.delete(*self.tree.get_children())
        self.progress_bar.config(maximum=len(self.proxies_loaded), value=0)

        self._log(f"[▶] Scan started on {len(self.proxies_loaded)} proxies (Threads: {threads}, Timeout: {timeout}s, Mode: {mode.upper()})")
        self.lbl_status.config(text=f"Scanning active... Threads: {threads} | Protocol: {mode.upper()}")

        # Launch background orchestrator thread
        self.worker_thread = threading.Thread(
            target=self._run_scan_worker,
            args=(list(self.proxies_loaded), mode, threads, timeout, pre_ping),
            daemon=True
        )
        self.worker_thread.start()

    def _on_stop_scan(self):
        if not self.is_running:
            return
        self._log("[⏹] Stopping scan... Gracefully finalizing current active threads...")
        self.lbl_status.config(text="Stopping scan...")
        self.stop_event.set()
        self.btn_stop.config(state="disabled")

    def _on_clear_results(self):
        if self.is_running:
            messagebox.showwarning("Running", "Please stop the scan before clearing results.")
            return
        self.tree.delete(*self.tree.get_children())
        self.alive_results.clear()
        self.card_labels["ALIVE"].config(text="0")
        self.card_labels["DEAD"].config(text="0")
        self.card_labels["SOCKS5"].config(text="0")
        self.card_labels["SOCKS4"].config(text="0")
        self.card_labels["HTTP"].config(text="0")
        self.card_labels["TIME"].config(text="00:00")
        self.progress_bar.config(value=0)
        self.lbl_progress_pct.config(text="0% (0/0)")
        self.lbl_status.config(text="Cleared results.")

    # ------------------------------------------------------------------------
    # BACKGROUND SCAN WORKER
    # ------------------------------------------------------------------------
    def _run_scan_worker(self, proxies: List[ProxyItem], mode: str, threads: int, timeout: int, pre_ping: bool):
        engine = ProxyCheckerEngine(timeout=timeout, pre_ping=pre_ping)
        res_manager = ResultsManager(output_dir=SCRIPT_DIR)

        def check_one(item: ProxyItem):
            if self.stop_event.is_set():
                return None
            force_p = None if mode == "auto" else mode
            res = engine.check_proxy(item, force_proto=force_p)
            return res

        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_item = {executor.submit(check_one, p): p for p in proxies}
            for future in as_completed(future_to_item):
                if self.stop_event.is_set():
                    break
                try:
                    res = future.result()
                    if res:
                        if res.alive:
                            res_manager.record_alive(res)
                        self.msg_queue.put(("RESULT", res))
                except Exception as e:
                    self.msg_queue.put(("LOG", f"Worker error: {e}"))

        # Finalize reports
        elapsed = time.time() - self.start_time
        res_manager.finalize_reports(total_checked=self.checked_count, elapsed_sec=elapsed)
        self.msg_queue.put(("SCAN_FINISHED", elapsed))

    # ------------------------------------------------------------------------
    # QUEUE POLLER (RUNS SAFELY ON TKINTER MAIN THREAD)
    # ------------------------------------------------------------------------
    def _process_queue(self):
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                mtype = msg[0]

                if mtype == "RESULT":
                    res: CheckResult = msg[1]
                    self.checked_count += 1

                    if res.alive:
                        self.alive_count += 1
                        self.alive_results.append(res)

                        if "SOCKS5" in res.protocol:
                            self.socks5_count += 1
                        elif "SOCKS4" in res.protocol:
                            self.socks4_count += 1
                        elif "HTTP" in res.protocol:
                            self.http_count += 1

                        self._insert_table_row(res)
                    else:
                        self.dead_count += 1
                        if not self.filter_alive_only.get():
                            self._insert_table_row(res)

                    # Update counters
                    self.card_labels["ALIVE"].config(text=str(self.alive_count))
                    self.card_labels["DEAD"].config(text=str(self.dead_count))
                    self.card_labels["SOCKS5"].config(text=str(self.socks5_count))
                    self.card_labels["SOCKS4"].config(text=str(self.socks4_count))
                    self.card_labels["HTTP"].config(text=str(self.http_count))

                    # Update Progress
                    total = len(self.proxies_loaded) or 1
                    pct = int((self.checked_count / total) * 100)
                    self.progress_bar.config(value=self.checked_count)
                    self.lbl_progress_pct.config(text=f"{pct}% ({self.checked_count}/{total})")

                elif mtype == "LOG":
                    self._log(msg[1])

                elif mtype == "BASELINE_IP":
                    ip = msg[1]
                    self.lbl_ip_baseline.config(text=f"Real IP: {ip} [Protected]")

                elif mtype == "HARVEST_DONE":
                    parsed_list = msg[1]
                    self.proxies_loaded = parsed_list
                    self.card_labels["TOTAL"].config(text=str(len(parsed_list)))
                    self._log(f"[+] Harvester finished: Loaded {len(parsed_list)} fresh public proxies!")
                    self.lbl_status.config(text=f"Harvester ready: {len(parsed_list)} proxies loaded.")
                    messagebox.showinfo("Harvest Complete", f"Successfully scraped {len(parsed_list)} fresh proxies!")

                elif mtype == "SCAN_FINISHED":
                    elapsed = msg[1]
                    self.is_running = False
                    self.btn_start.config(state="normal")
                    self.btn_stop.config(state="disabled")
                    self._log(f"[✓] Scan Complete! Total: {self.checked_count} | Alive: {self.alive_count} | Elapsed: {elapsed:.2f}s")
                    self._log(f"[💾] Results saved to: {os.path.join(SCRIPT_DIR, 'results.txt')}")
                    self.lbl_status.config(text=f"Audit complete. {self.alive_count} alive proxies saved to results.txt")

        except queue.Empty:
            pass

        # Update timer display while running
        if self.is_running:
            sec = int(time.time() - self.start_time)
            m, s = divmod(sec, 60)
            self.card_labels["TIME"].config(text=f"{m:02d}:{s:02d}")

        self.root.after(40, self._process_queue)

    # ------------------------------------------------------------------------
    # TABLE VIEW HELPERS
    # ------------------------------------------------------------------------
    def _insert_table_row(self, res: CheckResult):
        row_id = len(self.tree.get_children()) + 1
        speed_str = f"{res.latency_ms}ms" if res.alive else "--"
        ssl_str = "YES" if res.ssl_support else ("NO" if res.alive else "--")
        country_str = f"{res.country_code} - {res.country}" if res.alive else "--"

        # Determine color tag
        if res.alive:
            if res.anonymity == "Elite":
                tag = "alive_elite"
            elif res.anonymity == "Anonymous":
                tag = "alive_anon"
            else:
                tag = "alive_trans"
        else:
            tag = "dead"

        self.tree.insert(
            "",
            0,
            values=(
                row_id,
                res.proxy,
                res.protocol,
                "ALIVE" if res.alive else "DEAD",
                speed_str,
                res.anonymity if res.alive else "--",
                ssl_str,
                country_str,
                res.isp if res.alive else "--"
            ),
            tags=(tag,)
        )

    def _refresh_table_view(self):
        self.tree.delete(*self.tree.get_children())
        alive_only = self.filter_alive_only.get()
        if alive_only:
            for r in reversed(self.alive_results):
                self._insert_table_row(r)
        else:
            # Re-insert alive
            for r in reversed(self.alive_results):
                self._insert_table_row(r)

    def _show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _copy_selected_proxy(self):
        sel = self.tree.selection()
        if not sel:
            return
        val = self.tree.item(sel[0], "values")
        if val and len(val) > 1:
            self.root.clipboard_clear()
            self.root.clipboard_append(val[1])

    def _copy_selected_url(self):
        sel = self.tree.selection()
        if not sel:
            return
        val = self.tree.item(sel[0], "values")
        if val and len(val) > 2:
            proto = val[2].lower()
            proxy = val[1]
            url = f"{proto}://{proxy}"
            self.root.clipboard_clear()
            self.root.clipboard_append(url)

    def _copy_selected_row(self):
        sel = self.tree.selection()
        if not sel:
            return
        val = self.tree.item(sel[0], "values")
        if val:
            line = " | ".join(str(x) for x in val)
            self.root.clipboard_clear()
            self.root.clipboard_append(line)

    def _copy_all_alive(self):
        if not self.alive_results:
            messagebox.showinfo("No Alive Proxies", "No alive proxies found yet to copy.")
            return
        lines = [r.formatted_line() for r in self.alive_results]
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(lines))
        messagebox.showinfo("Copied", f"Copied {len(lines)} alive proxy URLs to clipboard!")

    def _on_export_dialog(self):
        if not self.alive_results:
            messagebox.showinfo("Export", "No alive proxies to export yet.")
            return

        path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("JSON File", "*.json"), ("CSV File", "*.csv")],
            initialdir=SCRIPT_DIR
        )
        if not path:
            return

        try:
            if path.endswith(".json"):
                import json
                from dataclasses import asdict
                data = [asdict(r) for r in self.alive_results]
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            elif path.endswith(".csv"):
                import csv
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["Proxy", "Protocol", "IP", "Port", "Latency", "Anonymity", "SSL", "Country", "ISP"])
                    for r in self.alive_results:
                        w.writerow([r.proxy, r.protocol, r.ip, r.port, r.latency_ms, r.anonymity, r.ssl_support, r.country, r.isp])
            else:
                with open(path, "w", encoding="utf-8") as f:
                    for r in self.alive_results:
                        f.write(f"{r.formatted_line()} | {r.anonymity} | {r.latency_ms}ms | {r.country} | {r.isp}\n")

            messagebox.showinfo("Export Successful", f"Successfully exported {len(self.alive_results)} proxies to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error saving file: {e}")

    def _log(self, text: str):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, timestamp + text + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def _on_close(self):
        if self.is_running:
            if messagebox.askyesno("Exit Confirmation", "Scan is currently active. Do you really want to exit?"):
                self.stop_event.set()
                self.root.destroy()
        else:
            self.root.destroy()


# ============================================================================
# MAIN LAUNCHER
# ============================================================================
def main():
    root = tk.Tk()
    # High-DPI scaling awareness on Windows
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    app = M4DIUciH4ProxyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
