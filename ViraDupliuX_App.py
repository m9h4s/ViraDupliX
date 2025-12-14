import os
import hashlib
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import datetime
from collections import defaultdict
import subprocess
import platform
import stat
import csv
import math
import webbrowser  # برای باز کردن لینک‌ها

# --- کتابخانه‌های جانبی ---
try:
    from send2trash import send2trash
    SAFE_DELETE = True
except ImportError:
    SAFE_DELETE = False

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
    BaseRoot = TkinterDnD.Tk
except ImportError:
    HAS_DND = False
    BaseRoot = tk.Tk
    print("هشدار: کتابخانه tkinterdnd2 پیدا نشد. قابلیت Drag & Drop غیرفعال است.")

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("نکته: برای پیش‌نمایش ویدیو کتابخانه opencv-python را نصب کنید.")

# --- تنظیمات پیش‌فرض ---
DEFAULT_IGNORE = [
    "node_modules", ".git", "__pycache__", "venv", "env", ".venv", ".env", 
    "Windows", "Program Files", "Program Files (x86)", "$RECYCLE.BIN", "System Volume Information",
    ".idea", ".vscode", "dist", "build", "target", "Android", "obj", "bin"
]

EXTENSIONS_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".ico", ".webp", ".heic"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma", ".amr"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".csv", ".rtf", ".odt"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".cab"],
    "Code & Web": [
        ".html", ".htm", ".css", ".js", ".py", ".pyw", ".json", ".xml", ".php", ".sql", 
        ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rb", ".ts", ".vue", ".asp", ".aspx"
    ],
    "Executables": [".exe", ".msi", ".bat", ".cmd", ".sh", ".apk", ".jar", ".bin", ".app"],
    "Design & Fonts": [".psd", ".ai", ".svg", ".eps", ".indd", ".cdr", ".ttf", ".otf", ".woff", ".woff2"]
}

# --- تنظیمات زبان (به‌روزرسانی شده) ---
TRANSLATIONS = {
    "fa": {
        "app_title": "ViraDupliX - یابنده فایل‌های تکراری",
        "header": "ViraDupliX",
        "theme_dark": "🌙 حالت شب",
        "theme_light": "☀ حالت روز",
        "lang_switch": "English",
        "path_lbl": "📂 مسیر اسکن:",
        "browse_btn": "انتخاب پوشه",
        "filter_lbl": "فیلتر فرمت‌ها:",
        "ext_lbl": "پسوند خاص (مثلا .iso):",
        "ignore_lbl": "نادیده گرفتن (با کاما):",
        "ops_lbl": "عملیات:",
        "start_btn": "شروع اسکن ▶",
        "stop_btn": "توقف ⏹",
        "col_name": "نام فایل",
        "col_size": "حجم",
        "col_date": "تاریخ",
        "col_path": "مسیر",
        "preview_title": "👁 پیش‌نمایش",
        "no_preview": "پیش‌نمایش موجود نیست",
        "sel_size": "انتخاب شده: ",
        "auto_sel": "انتخاب هوشمند",
        "export_csv": "خروجی CSV",
        "stats": "نمایش آمار",
        "about_btn": "درباره ما",  # دکمه جدید
        "del_btn": "🗑 حذف انتخاب‌ها",
        "status_ready": "آماده",
        "status_scanning": "در حال اسکن...",
        "msg_del_confirm": "آیا فایل‌های انتخاب شده حذف شوند؟",
        "msg_del_success": "فایل پاک شد.",
        "group_txt": "📂 گروه",
        "disk_free": "آزاد",
        "disk_total": "کل",
        "disk_title": "فضای دیسک",
        "status_done": "پایان. {0} گروه پیدا شد. فضای قابل آزادسازی: {1}",
        "msg_success_title": "موفقیت",
        "msg_saved": "خروجی ذخیره شد.",
        "msg_error_title": "خطا",
        "msg_no_data": "داده‌ای برای خروجی وجود ندارد.",
        "msg_scan_first": "لطفا ابتدا اسکن انجام دهید.",
        "stats_title": "آمار اسکن",
        "stats_header": "خلاصه فضای قابل آزادسازی",
        "stats_desc": "فضای قابل آزادسازی با حذف تکراری‌ها",
        "suffix_del": " [❌ حذف]",
        "suffix_keep": " [✔ اصلی]",
        "res_del": "نتیجه",
        "res_del_msg": "{0} فایل پاک شد.",
        
        # --- بخش درباره ما (فارسی) ---
        "about_title": "درباره برنامه",
        "dev_lbl": "توسعه‌دهنده:",
        "company_lbl": "شرکت:",
        "version_lbl": "نسخه برنامه:",
        "date_lbl": "تاریخ ایجاد:",
        "github_lbl": "گیت‌هاب:",

        "donate_lbl": "حمایت مالی:",
        "donate_val": "☕ خرید قهوه (Coffeete)",
        "btn_donate": "☕ حمایت مالی",

        "date_val": "یکشنبه 23 آذر 1404\nساعت 12:30 ظهر",
        "dev_name": "محمد حسین سلیمانی",
        "company_name": "ویرا افزار تاراز",
        "version_val": "1.0.0"
    },
    "en": {
        "app_title": "ViraDupliX - Duplicate Finder",
        "header": "ViraDupliX",
        "theme_dark": "🌙 Dark Mode",
        "theme_light": "☀ Light Mode",
        "lang_switch": "فارسی",
        "path_lbl": "📂 Scan Path:",
        "browse_btn": "Browse Folder",
        "filter_lbl": "File Filters:",
        "ext_lbl": "Custom Ext (e.g. .iso):",
        "ignore_lbl": "Ignore Folders (comma):",
        "ops_lbl": "Operations:",
        "start_btn": "Start Scan ▶",
        "stop_btn": "Stop ⏹",
        "col_name": "Filename",
        "col_size": "Size",
        "col_date": "Date",
        "col_path": "Path",
        "preview_title": "👁 Preview",
        "no_preview": "No Preview Available",
        "sel_size": "Selected: ",
        "auto_sel": "Auto Select",
        "export_csv": "Export CSV",
        "stats": "Show Stats",
        "about_btn": "About", # New Button
        "del_btn": "🗑 Delete Selected",
        "status_ready": "Ready",
        "status_scanning": "Scanning...",
        "msg_del_confirm": "Delete selected files?",
        "msg_del_success": "Files deleted.",
        "group_txt": "📂 Group",
        "disk_free": "Free",
        "disk_total": "Total",
        "disk_title": "Disk Info",
        "status_done": "Finished. {0} groups found. Reclaimable space: {1}",
        "msg_success_title": "Success",
        "msg_saved": "Export saved successfully.",
        "msg_error_title": "Error",
        "msg_no_data": "No data to export.",
        "msg_scan_first": "Please scan first.",
        "stats_title": "Scan Statistics",
        "stats_header": "Reclaimable Space Summary",
        "stats_desc": "Space to be freed by deleting duplicates",
        "suffix_del": " [❌ Delete]",
        "suffix_keep": " [✔ Original]",
        "res_del": "Result",
        "res_del_msg": "{0} files deleted.",

        # --- About Section (English) ---
        "about_title": "About App",
        "dev_lbl": "Developer:",
        "company_lbl": "Company:",
        "version_lbl": "Version:",
        "date_lbl": "Created Date:",
        "github_lbl": "GitHub:",

        "donate_lbl": "Support:",
        "donate_val": "☕ Buy me a coffee",
        "btn_donate": "☕ Donate",

        "date_val": "Sunday, December 14, 2025\n12:30 PM",
        "dev_name": "Mohammad Hossein Soleymani",
        "company_name": "Vira Afzar Taraz",
        "version_val": "1.0.0"
    }
}

class BeautifulDuplicateFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("ViraDupliX Ultimate - Duplicate Finder")
        self.root.geometry("1300x850")
        
        # --- FIX: Taskbar Icon ---
        if platform.system() == "Windows":
            try:
                import ctypes
                myappid = 'viraduplix.duplicate.finder.v1'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception as e:
                print(e)
        # -------------------------

        self.is_dark = False
        self.current_lang = "fa"
        self.colors = {
            "bg": "#f0f2f5", "fg": "#000000", "header": "#37474f", "header_fg": "white",
            "panel": "white", "tree_bg": "white", "tree_fg": "black", "select": "#E3F2FD"
        }
        
        self.load_icon()

        self.folder_path = tk.StringVar()
        self.stop_event = threading.Event()
        self.scan_thread = None
        self.total_scanned_size = 0
        
        self.filter_vars = {}
        for key in EXTENSIONS_MAP.keys():
            self.filter_vars[key] = tk.BooleanVar(value=True)
        
        self.custom_ext_var = tk.StringVar()
        self.ignore_list_var = tk.StringVar(value=", ".join(DEFAULT_IGNORE))

        self.create_layout()
        self.setup_styles()
            
        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.drop_handler)

    def load_icon(self):
        try:
            if os.path.exists("logo.ico"): self.root.iconbitmap("logo.ico")
            if os.path.exists("logo.png") and HAS_PIL:
                icon_img = ImageTk.PhotoImage(file="logo.png")
                self.root.iconphoto(True, icon_img)
        except: pass

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.update_theme_styles()

    def update_theme_styles(self):
        bg = "#2d2d2d" if self.is_dark else "#ffffff"
        fg = "#ffffff" if self.is_dark else "#000000"
        select_bg = "#444444" if self.is_dark else "#E3F2FD"
        
        self.style.configure("Treeview", background=bg, foreground=fg, fieldbackground=bg, rowheight=30)
        self.style.map("Treeview", background=[("selected", select_bg)], foreground=[("selected", fg)])
        self.style.configure("Treeview.Heading", background="#455A64", foreground="white", relief="flat")
        
        if self.is_dark:
            color_del_bg = "#4a1818"
            color_del_fg = "#ff9999"
            color_keep_bg = "#1b3a1b"
            color_keep_fg = "#a5d6a7"
        else:
            color_del_bg = "#ffebee"
            color_del_fg = "#c62828"
            color_keep_bg = "#e8f5e9"
            color_keep_fg = "#2e7d32"

        self.tree.tag_configure('checked', background=color_del_bg, foreground=color_del_fg)
        self.tree.tag_configure('keeper', background=color_keep_bg, foreground=color_keep_fg)
        self.tree.tag_configure('unchecked', background=bg, foreground=fg)
        self.tree.tag_configure('group', background='#cfd8dc', foreground='#37474f')

        self.style.configure("TButton", padding=6)
        self.style.configure("Primary.TButton", background="#2196F3", foreground="white")
        self.style.configure("Success.TButton", background="#4CAF50", foreground="white")
        self.style.configure("Danger.TButton", background="#F44336", foreground="white")
        
        self.root.configure(bg=self.colors["bg"])

    def create_layout(self):
        self.header_frame = tk.Frame(self.root, bg=self.colors["header"], pady=10, padx=20)
        self.header_frame.pack(fill="x")
        
        self.lbl_header = tk.Label(self.header_frame, text="", bg=self.colors["header"], fg="white", font=("Segoe UI", 18, "bold"))
        self.lbl_header.pack(side="left")
        
        self.btn_lang = tk.Button(self.header_frame, command=self.toggle_language, bg="#546E7A", fg="white", bd=0, padx=10)
        self.btn_lang.pack(side="right", padx=5)

        self.btn_theme = tk.Button(self.header_frame, command=self.toggle_theme, bg="#546E7A", fg="white", bd=0, padx=10)
        self.btn_theme.pack(side="right")

        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=10, pady=10)

        # Left Panel
        self.settings_frame = tk.Frame(main_paned, bg=self.colors["panel"], width=280, padx=10, pady=10)
        main_paned.add(self.settings_frame, weight=1)

        self.lbl_path = tk.Label(self.settings_frame, bg=self.colors["panel"], font=("Segoe UI", 10, "bold"))
        self.lbl_path.pack(anchor="w", pady=(0,5))
        
        self.entry_path = tk.Entry(self.settings_frame, textvariable=self.folder_path, bg="#fafafa")
        self.entry_path.pack(fill="x", pady=(0,5))
        
        self.btn_browse = tk.Button(self.settings_frame, command=self.browse_folder, bg="#eee")
        self.btn_browse.pack(fill="x", pady=(0, 15))

        self.lbl_filter = tk.Label(self.settings_frame, bg=self.colors["panel"], font=("Segoe UI", 10, "bold"))
        self.lbl_filter.pack(anchor="w")
        
        filters_frame = tk.Frame(self.settings_frame, bg=self.colors["panel"])
        filters_frame.pack(fill="x", pady=5)
        for key, var in self.filter_vars.items():
            cb = tk.Checkbutton(filters_frame, text=key, variable=var, bg=self.colors["panel"], anchor="w", selectcolor=self.colors["panel"])
            cb.pack(fill="x", anchor="w")
        
        self.lbl_ext = tk.Label(self.settings_frame, bg=self.colors["panel"], font=("Segoe UI", 9))
        self.lbl_ext.pack(anchor="w", pady=(10,0))
        tk.Entry(self.settings_frame, textvariable=self.custom_ext_var, bg="#fafafa").pack(fill="x")

        self.lbl_ignore = tk.Label(self.settings_frame, bg=self.colors["panel"], font=("Segoe UI", 10, "bold"))
        self.lbl_ignore.pack(anchor="w", pady=(15,5))
        tk.Entry(self.settings_frame, textvariable=self.ignore_list_var, bg="#fafafa").pack(fill="x")

        self.lbl_ops = tk.Label(self.settings_frame, bg=self.colors["panel"], font=("Segoe UI", 10, "bold"))
        self.lbl_ops.pack(anchor="w", pady=(20,5))
        
        self.btn_start = ttk.Button(self.settings_frame, command=self.start_scan_thread, style="Success.TButton")
        self.btn_start.pack(fill="x", pady=2)
        self.btn_stop = ttk.Button(self.settings_frame, command=self.stop_scan, state="disabled", style="Danger.TButton")
        self.btn_stop.pack(fill="x", pady=2)
        
        self.disk_info_lbl = tk.Label(self.settings_frame, text="", bg=self.colors["panel"], fg="#757575", font=("Segoe UI", 8), wraplength=200)
        self.disk_info_lbl.pack(fill="x", pady=20)

        # Center Panel
        center_frame = tk.Frame(main_paned, bg=self.colors["bg"])
        main_paned.add(center_frame, weight=4)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(center_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x")

        columns = ("Size", "Date", "Path")
        self.tree = ttk.Treeview(center_frame, columns=columns, show="tree headings", selectmode="browse")
        self.tree.column("#0", width=250)
        self.tree.column("Size", width=80, anchor="center")
        self.tree.column("Date", width=120, anchor="center")
        
        vsb = ttk.Scrollbar(center_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<ButtonRelease-1>", self.on_select_item)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Right Panel
        self.preview_frame = tk.Frame(main_paned, bg=self.colors["panel"], width=300)
        main_paned.add(self.preview_frame, weight=1)
        
        self.lbl_preview_title = tk.Label(self.preview_frame, bg=self.colors["panel"], font=("Segoe UI", 10, "bold"))
        self.lbl_preview_title.pack(pady=10)
        
        self.lbl_preview_img = tk.Label(self.preview_frame, bg="#eceff1", width=30, height=15)
        self.lbl_preview_img.image = None # FIX Attribute Error
        self.lbl_preview_img.pack(padx=10, pady=10, fill="both", expand=False)
        
        self.txt_preview = tk.Text(self.preview_frame, height=15, width=30, bg="#fafafa", font=("Consolas", 9), state="disabled", wrap="word")
        
        self.lbl_preview_info = tk.Label(self.preview_frame, text="", bg=self.colors["panel"], justify="left", wraplength=250)
        self.lbl_preview_info.pack(padx=10, pady=5)

        # Bottom Panel
        bottom_panel = tk.Frame(self.root, bg=self.colors["panel"], height=60, padx=20, pady=10)
        bottom_panel.pack(fill="x", side="bottom")

        self.lbl_selected_size = tk.Label(bottom_panel, bg=self.colors["panel"], fg="#d32f2f", font=("Segoe UI", 11, "bold"))
        self.lbl_selected_size.pack(side="left")

        self.btn_auto = ttk.Button(bottom_panel, command=self.auto_select, style="Primary.TButton")
        self.btn_auto.pack(side="right", padx=5)
        
        self.btn_export = ttk.Button(bottom_panel, command=self.export_csv)
        self.btn_export.pack(side="right", padx=5)
        
        self.btn_stats = ttk.Button(bottom_panel, command=self.show_stats_popup)
        self.btn_stats.pack(side="right", padx=5)

        self.btn_donate_main = ttk.Button(bottom_panel, command=lambda: webbrowser.open("https://www.coffeete.ir/mhsoleymani"))
        self.btn_donate_main.pack(side="right", padx=5)

        # +++ About Button +++
        self.btn_about = ttk.Button(bottom_panel, command=self.show_about_popup)
        self.btn_about.pack(side="right", padx=5)
        
        self.btn_delete = ttk.Button(bottom_panel, command=self.delete_selected, style="Danger.TButton")
        self.btn_delete.pack(side="left", padx=20)
        
        self.status_lbl = tk.Label(self.root, bg="#455A64", fg="white", anchor="e", padx=10)
        self.status_lbl.pack(side="bottom", fill="x")

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Open Folder", command=self.open_file_folder)
        self.context_menu.add_command(label="Open File", command=self.open_file_direct)

        self.update_texts()

    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "fa" else "fa"
        self.update_texts()

    def update_texts(self):
        T = TRANSLATIONS[self.current_lang]
        
        self.root.title(T["app_title"])
        self.lbl_header.config(text=T["header"])
        self.btn_lang.config(text=T["lang_switch"])
        self.btn_theme.config(text=T["theme_dark"] if not self.is_dark else T["theme_light"])
        
        self.lbl_path.config(text=T["path_lbl"])
        self.btn_browse.config(text=T["browse_btn"])
        self.lbl_filter.config(text=T["filter_lbl"])
        self.lbl_ext.config(text=T["ext_lbl"])
        self.lbl_ignore.config(text=T["ignore_lbl"])
        self.lbl_ops.config(text=T["ops_lbl"])
        self.btn_start.config(text=T["start_btn"])
        self.btn_stop.config(text=T["stop_btn"])
        
        self.tree.heading("#0", text=T["col_name"])
        self.tree.heading("Size", text=T["col_size"])
        self.tree.heading("Date", text=T["col_date"])
        self.tree.heading("Path", text=T["col_path"])
        
        self.lbl_preview_title.config(text=T["preview_title"])
        if not self.lbl_preview_img.image:
            self.lbl_preview_img.config(text=T["no_preview"])
            
        self.lbl_selected_size.config(text=T["sel_size"] + "0 KB")
        self.btn_auto.config(text=T["auto_sel"])
        self.btn_export.config(text=T["export_csv"])
        self.btn_stats.config(text=T["stats"])
        self.btn_donate_main.config(text=T["btn_donate"])
        self.btn_about.config(text=T["about_btn"]) # Update about text
        self.btn_delete.config(text=T["del_btn"])
        self.status_lbl.config(text=T["status_ready"])
        
        self.update_disk_usage()

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        
        if self.is_dark:
            self.colors.update({"bg": "#1e1e1e", "fg": "#ffffff", "header": "#263238", "panel": "#2d2d2d", "tree_bg": "#2d2d2d"})
            self.btn_theme.config(text="☀ Light Mode")
        else:
            self.colors.update({"bg": "#f0f2f5", "fg": "#000000", "header": "#37474f", "panel": "#ffffff", "tree_bg": "#ffffff"})
            self.btn_theme.config(text="🌙 Dark Mode")
        
        self.header_frame.config(bg=self.colors["header"])
        self.settings_frame.config(bg=self.colors["panel"])
        self.preview_frame.config(bg=self.colors["panel"])
        self.lbl_preview_info.config(bg=self.colors["panel"], fg=self.colors["fg"])
        self.lbl_selected_size.config(bg=self.colors["panel"])
        
        self.apply_theme_to_children(self.settings_frame)
        self.apply_theme_to_children(self.preview_frame)
        
        self.update_theme_styles()

    def apply_theme_to_children(self, widget):
        try:
            for child in widget.winfo_children():
                if isinstance(child, (tk.Label, tk.Checkbutton, tk.Frame)):
                    child.config(bg=self.colors["panel"])
                    if hasattr(child, "config") and "fg" in child.keys():
                        child.config(fg=self.colors["fg"])
                    
                    if isinstance(child, tk.Checkbutton):
                        child.config(selectcolor=self.colors["panel"])
                
                if isinstance(child, tk.Frame):
                    self.apply_theme_to_children(child)
        except: pass

    # --- About Popup Logic ---
    def show_about_popup(self):
        T = TRANSLATIONS[self.current_lang]
        
        top = tk.Toplevel(self.root)
        top.title(T["about_title"])
        top.geometry("450x550")
        top.configure(bg="white")
        top.resizable(False, False)

        # Logo
        if HAS_PIL and (os.path.exists("logo.png") or os.path.exists("logo.ico")):
            try:
                img_path = "logo.png" if os.path.exists("logo.png") else "logo.ico"
                img = Image.open(img_path)
                img.thumbnail((80, 80))
                photo = ImageTk.PhotoImage(img)
                lbl_img = tk.Label(top, image=photo, bg="white")
                lbl_img.image = photo
                lbl_img.pack(pady=(20, 10))
            except: pass
        
        tk.Label(top, text="ViraDupliX", font=("Segoe UI", 16, "bold"), bg="white", fg="#37474f").pack()

        # Content Frame
        content_frame = tk.Frame(top, bg="white", padx=20, pady=10)
        content_frame.pack(fill="both", expand=True)

        def create_link(parent, label_txt, link_text, url):
            f = tk.Frame(parent, bg="white")
            f.pack(fill="x", pady=5)
            tk.Label(f, text=label_txt, font=("Segoe UI", 9, "bold"), bg="white").pack(side="left" if self.current_lang=="en" else "right")
            
            link = tk.Label(f, text=link_text, font=("Segoe UI", 9, "underline"), fg="blue", bg="white", cursor="hand2")
            link.pack(side="left" if self.current_lang=="en" else "right", padx=5)
            link.bind("<Button-1>", lambda e: webbrowser.open(url))

        def create_info(parent, label_txt, value_txt):
            f = tk.Frame(parent, bg="white")
            f.pack(fill="x", pady=5)
            tk.Label(f, text=label_txt, font=("Segoe UI", 9, "bold"), bg="white").pack(side="left" if self.current_lang=="en" else "right")
            tk.Label(f, text=value_txt, font=("Segoe UI", 9), bg="white").pack(side="left" if self.current_lang=="en" else "right", padx=5)

        # Developer
        create_link(content_frame, T["dev_lbl"], T["dev_name"], "https://mhsoleymani.ir/")
        
        # Company
        create_link(content_frame, T["company_lbl"], T["company_name"], "https://codingtaraz.com/")

        # GitHub
        create_link(content_frame, T["github_lbl"], "m9h4s", "https://github.com/m9h4s")

        # Donate
        create_link(content_frame, T["donate_lbl"], T["donate_val"], "https://www.coffeete.ir/mhsoleymani")

        tk.Frame(content_frame, height=2, bg="#eee").pack(fill="x", pady=10)

        # Version
        create_info(content_frame, T["version_lbl"], T["version_val"])

        # Date
        # For date, we center it
        tk.Label(content_frame, text=T["date_lbl"], font=("Segoe UI", 9, "bold"), bg="white").pack(pady=(10, 0))
        tk.Label(content_frame, text=T["date_val"], font=("Segoe UI", 9), bg="white", fg="#555").pack()

        # Copyright
        tk.Label(top, text="© 2025 ViraDupliX", font=("Segoe UI", 8), bg="white", fg="#999").pack(side="bottom", pady=10)

    # --- Other Methods ---
    def drop_handler(self, event):
        path = event.data
        if path.startswith('{') and path.endswith('}'): path = path[1:-1]
        if os.path.isdir(path):
            self.folder_path.set(path)
            self.update_disk_usage()

    def on_select_item(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = sel[0]
        vals = self.tree.item(item, "values")
        if not vals or len(vals) < 3: return
        
        path = vals[2]
        ext = os.path.splitext(path)[1].lower()
        
        info_text = f"{TRANSLATIONS[self.current_lang]['col_name']}: {os.path.basename(path)}\n" \
                    f"{TRANSLATIONS[self.current_lang]['col_size']}: {vals[0]}\n" \
                    f"Format: {ext}"
        self.lbl_preview_info.config(text=info_text)

        if HAS_PIL and ext in EXTENSIONS_MAP["Images"]:
            self.show_image_preview(path)
        elif HAS_PIL and HAS_CV2 and ext in EXTENSIONS_MAP["Videos"]:
            self.show_video_preview(path)
        elif ext in EXTENSIONS_MAP["Documents"] or ext in EXTENSIONS_MAP["Code & Web"] or ext == ".txt":
            self.show_text_preview(path)
        else:
            self.reset_preview_widgets()
            self.lbl_preview_img.config(image="", text=TRANSLATIONS[self.current_lang]["no_preview"], width=30, height=15)

    def reset_preview_widgets(self):
        self.txt_preview.pack_forget()
        self.lbl_preview_img.pack(padx=10, pady=10, fill="both", expand=False)
        self.lbl_preview_img.config(image="", width=0, height=0)

    def show_image_preview(self, path):
        self.reset_preview_widgets()
        try:
            img = Image.open(path)
            try: resample = Image.Resampling.LANCZOS
            except AttributeError: resample = Image.ANTIALIAS
            
            img.thumbnail((280, 280), resample)
            photo = ImageTk.PhotoImage(img)
            
            self.lbl_preview_img.config(image=photo, text="", width=0, height=0)
            self.lbl_preview_img.image = photo
        except:
            self.lbl_preview_img.config(image="", text="Error", width=30, height=15)

    def show_video_preview(self, path):
        self.reset_preview_widgets()
        try:
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                
                try: resample = Image.Resampling.LANCZOS
                except AttributeError: resample = Image.ANTIALIAS
                
                img.thumbnail((280, 280), resample)
                photo = ImageTk.PhotoImage(img)
                self.lbl_preview_img.config(image=photo, text="[VIDEO]", compound="bottom", width=0, height=0)
                self.lbl_preview_img.image = photo
            else:
                self.lbl_preview_img.config(text="Video Error", width=30, height=15)
        except Exception as e:
            self.lbl_preview_img.config(text="Codec Error", width=30, height=15)

    def show_text_preview(self, path):
        self.lbl_preview_img.pack_forget()
        self.txt_preview.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.txt_preview.config(state="normal")
        self.txt_preview.delete("1.0", tk.END)
        
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2000)
                self.txt_preview.insert("1.0", content)
        except Exception as e:
            self.txt_preview.insert("1.0", f"Error: {e}")
            
        self.txt_preview.config(state="disabled")

    def get_allowed_extensions(self):
        allowed = set()
        any_checked = False
        for cat, var in self.filter_vars.items():
            if var.get():
                any_checked = True
                for ext in EXTENSIONS_MAP[cat]: allowed.add(ext)
        
        custom = self.custom_ext_var.get().strip()
        if custom:
            any_checked = True
            for c in custom.split(','):
                c = c.strip()
                if not c.startswith('.'): c = '.' + c
                allowed.add(c.lower())
        
        if not any_checked: return None 
        return allowed

    def get_ignore_list(self):
        raw = self.ignore_list_var.get()
        return [x.strip().lower() for x in raw.split(',') if x.strip()]

    def scan_logic(self, folder_path):
        try:
            allowed_exts = self.get_allowed_extensions()
            ignore_folders = self.get_ignore_list()
            
            self.update_status(TRANSLATIONS[self.current_lang]["status_scanning"])
            all_files = []
            
            for root, dirs, files in os.walk(folder_path):
                if self.stop_event.is_set(): return
                dirs[:] = [d for d in dirs if d.lower() not in ignore_folders]
                
                for name in files:
                    ext = os.path.splitext(name)[1].lower()
                    if allowed_exts is not None and ext not in allowed_exts:
                        continue
                    all_files.append(os.path.join(root, name))
            
            if not all_files:
                self.finish_scan([])
                return

            size_map = defaultdict(list)
            for idx, fpath in enumerate(all_files):
                if self.stop_event.is_set(): return
                if idx % 1000 == 0: self.progress_var.set((idx / len(all_files)) * 20)
                try:
                    s = os.path.getsize(fpath)
                    if s > 0: size_map[s].append(fpath)
                except: pass
            
            candidates_size = [p for p in size_map.values() if len(p) > 1]
            
            candidates_ph = []
            total = len(candidates_size)
            if total == 0:
                self.finish_scan([])
                return

            for i, group in enumerate(candidates_size):
                if self.stop_event.is_set(): return
                self.progress_var.set(20 + (i/total)*30)
                temp_ph = defaultdict(list)
                for fpath in group:
                    ph = self.get_hash(fpath, True)
                    if ph: temp_ph[ph].append(fpath)
                for g in temp_ph.values():
                    if len(g) > 1: candidates_ph.append(g)

            final_dupes = []
            total = len(candidates_ph)
            for i, group in enumerate(candidates_ph):
                if self.stop_event.is_set(): return
                self.progress_var.set(50 + (i/total)*50)
                temp_fh = defaultdict(list)
                for fpath in group:
                    fh = self.get_hash(fpath, False)
                    if fh: temp_fh[fh].append(fpath)
                for g in temp_fh.values():
                    if len(g) > 1: final_dupes.append(g)

            self.finish_scan(final_dupes)

        except Exception as e:
            print(f"Error: {e}")
            self.update_status("Error!")
        finally:
            self.root.after(0, lambda: self.btn_start.config(state="normal"))
            self.root.after(0, lambda: self.btn_stop.config(state="disabled"))

    def get_hash(self, path, first_chunk):
        try:
            h = hashlib.md5()
            with open(path, "rb") as f:
                if first_chunk: h.update(f.read(4096))
                else:
                    while c := f.read(65536): h.update(c)
            return h.hexdigest()
        except: return None

    def start_scan_thread(self):
        path = self.folder_path.get()
        if not os.path.exists(path):
            messagebox.showerror("Error", "Invalid Path")
            return
        self.stop_event.clear()
        for item in self.tree.get_children(): self.tree.delete(item)
        self.progress_var.set(0)
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.scan_thread = threading.Thread(target=self.scan_logic, args=(path,), daemon=True)
        self.scan_thread.start()

    def stop_scan(self):
        if self.scan_thread and self.scan_thread.is_alive():
            self.stop_event.set()
            self.status_lbl.config(text="Stopping...")

    def finish_scan(self, results):
        self.root.after(0, lambda: self.populate_tree(results))

    def populate_tree(self, results):
        self.progress_var.set(100)
        total_wasted = 0
        T = TRANSLATIONS[self.current_lang]
        
        for idx, group in enumerate(results):
            f0 = group[0]
            sz = os.path.getsize(f0)
            wasted = sz * (len(group) - 1)
            total_wasted += wasted
            sz_str = self.format_bytes(sz)

            group_text = f"{T['group_txt']} {idx+1}" 
            pid = self.tree.insert("", "end", text=group_text, values=(sz_str, "", ""), open=True)
            self.tree.item(pid, tags=('group',))
            
            for i, path in enumerate(group):
                fname = os.path.basename(path)
                dt = datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d')
                iid = self.tree.insert(pid, "end", text=fname, values=(sz_str, dt, path))
                self.tree.item(iid, tags=('file', 'unchecked'))

        msg = T['status_done'].format(len(results), self.format_bytes(total_wasted))
        self.update_status(msg)
        self.total_scanned_size = total_wasted

    def update_disk_usage(self):
        path = self.folder_path.get()
        T = TRANSLATIONS[self.current_lang]
        if not path or not os.path.exists(path): 
            self.disk_info_lbl.config(text="")
            return
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            txt = f"{T['disk_title']}:\n{T['disk_free']}: {self.format_bytes(free)}\n{T['disk_total']}: {self.format_bytes(total)}"
            self.disk_info_lbl.config(text=txt)
        except: pass

    def export_csv(self):
        T = TRANSLATIONS[self.current_lang]
        if not self.tree.get_children():
            messagebox.showinfo(T["msg_error_title"], T["msg_no_data"])
            return
        
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not fpath: return
        
        try:
            with open(fpath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Group", "Filename", "Size", "Path"])
                
                for group in self.tree.get_children():
                    g_text = self.tree.item(group, "text")
                    for child in self.tree.get_children(group):
                        vals = self.tree.item(child, "values")
                        writer.writerow([g_text, self.tree.item(child, "text"), vals[0], vals[2]])
            messagebox.showinfo(T["msg_success_title"], T["msg_saved"])
        except Exception as e:
            messagebox.showerror(T["msg_error_title"], str(e))

    def show_stats_popup(self):
        T = TRANSLATIONS[self.current_lang]
        if self.total_scanned_size == 0:
            messagebox.showinfo(T["stats_title"], T["msg_scan_first"])
            return
            
        top = tk.Toplevel(self.root)
        top.title(T["stats_title"])
        top.geometry("400x300")
        top.configure(bg="white")
        
        tk.Label(top, text=T["stats_header"], bg="white", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        canvas = tk.Canvas(top, width=200, height=200, bg="white", highlightthickness=0)
        canvas.pack()
        
        canvas.create_oval(10, 10, 190, 190, fill="#e0e0e0", outline="")
        canvas.create_arc(10, 10, 190, 190, start=0, extent=-90, fill="#2196F3", outline="")
        
        lbl_size = tk.Label(top, text=f"{self.format_bytes(self.total_scanned_size)}", font=("Segoe UI", 16, "bold"), fg="#2196F3", bg="white")
        lbl_size.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(top, text=T["stats_desc"], bg="white").pack(pady=10)

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item: return
        tags = self.tree.item(item, "tags")
        if 'group' in tags: return
        
        if 'checked' in tags:
            self.mark_as_unchecked(item, is_keeper=False)
        else:
            self.mark_as_checked(item)
            
        self.update_selected_label()

    def mark_as_checked(self, item):
        T = TRANSLATIONS[self.current_lang]
        fname = self.tree.item(item, "text")
        # حذف پسوند‌های قبلی (چه فارسی چه انگلیسی)
        for bad_suffix in [" [❌ حذف]", " [❌ Delete]", " [✔ اصلی]", " [✔ Original]"]:
            fname = fname.replace(bad_suffix, "")
            
        self.tree.item(item, tags=('file', 'checked'), text=f"{fname}{T['suffix_del']}")

    def mark_as_unchecked(self, item, is_keeper=False):
        T = TRANSLATIONS[self.current_lang]
        fname = self.tree.item(item, "text")
        for bad_suffix in [" [❌ حذف]", " [❌ Delete]", " [✔ اصلی]", " [✔ Original]"]:
            fname = fname.replace(bad_suffix, "")
        
        if is_keeper:
            self.tree.item(item, tags=('file', 'keeper'), text=f"{fname}{T['suffix_keep']}")
        else:
            self.tree.item(item, tags=('file', 'unchecked'), text=fname)

    def auto_select(self):
        for parent in self.tree.get_children():
            children = self.tree.get_children(parent)
            if not children: continue
            data = []
            for child in children:
                path = self.tree.item(child, "values")[2]
                try: data.append((child, os.path.getctime(path)))
                except: data.append((child, 0))
            
            data.sort(key=lambda x: x[1])
            keeper = data[0][0]
            
            for child, _ in data:
                if child == keeper: self.mark_as_unchecked(child, True)
                else: self.mark_as_checked(child)
        self.update_selected_label()

    def update_selected_label(self):
        total = 0
        for p in self.tree.get_children():
            for c in self.tree.get_children(p):
                if 'checked' in self.tree.item(c, "tags"):
                    path = self.tree.item(c, "values")[2]
                    try: total += os.path.getsize(path)
                    except: pass
        T = TRANSLATIONS[self.current_lang]
        self.lbl_selected_size.config(text=f"{T['sel_size']}{self.format_bytes(total)}")

    def delete_selected(self):
        T = TRANSLATIONS[self.current_lang]
        to_del = []
        for p in self.tree.get_children():
            for c in self.tree.get_children(p):
                if 'checked' in self.tree.item(c, "tags"):
                    to_del.append((c, self.tree.item(c, "values")[2]))
        
        if not to_del: return
        
        if messagebox.askyesno(T["msg_error_title"] if "Error" in T["msg_error_title"] else "Confirm", f"{T['msg_del_confirm']}"):
            count = 0
            for iid, raw_path in to_del:
                path = os.path.normpath(raw_path)
                try:
                    os.chmod(path, stat.S_IWRITE)
                    if SAFE_DELETE: send2trash(path)
                    else: os.remove(path)
                    self.tree.delete(iid)
                    count += 1
                except Exception as e: print(e)
            
            for p in self.tree.get_children():
                if not self.tree.get_children(p): self.tree.delete(p)
            
            self.update_selected_label()
            messagebox.showinfo(T["res_del"], T["res_del_msg"].format(count))

    def update_status(self, txt):
        self.root.after(0, lambda: self.status_lbl.config(text=txt))

    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def browse_folder(self):
        p = filedialog.askdirectory()
        if p:
            self.folder_path.set(p)
            self.update_disk_usage()
            
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            if 'file' in self.tree.item(item, "tags"):
                self.context_menu.post(event.x_root, event.y_root)

    def open_file_folder(self):
        sel = self.tree.selection()
        if sel:
            path = self.tree.item(sel[0], "values")[2]
            if platform.system() == "Windows": subprocess.Popen(f'explorer /select,"{os.path.normpath(path)}"')
            else: subprocess.Popen(["xdg-open", os.path.dirname(path)])

    def open_file_direct(self):
        sel = self.tree.selection()
        if sel:
            path = self.tree.item(sel[0], "values")[2]
            if platform.system() == "Windows": os.startfile(path)
            else: subprocess.Popen(["xdg-open", path])

if __name__ == "__main__":
    root = BaseRoot()
    app = BeautifulDuplicateFinder(root)
    root.mainloop()
