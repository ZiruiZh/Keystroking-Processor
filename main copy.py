import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from lxml import etree
from docx import Document
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageSequenceClip
import tkinter.font as tkfont
import tempfile
import threading
import sys
import json
import queue
import time

# Placeholder imports for future implementation
# from lxml import etree
# from moviepy.editor import ImageSequenceClip
# from PIL import Image, ImageDraw, ImageFont

class XMLToVideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Analysis Workstation 1.0")
        self.root.configure(bg="#2b2b2b")
        self.root.geometry("1400x900")
        
        # Initialize variables
        self.xml_path = None
        self.word_path = None
        self.data_txt_path = None
        self.idfx_path = None
        self.xml_queue = []
        self.data_queue = []
        self.file_queue = []
        self.processing = False
        
        # Create menu bar first
        self.create_menu_bar()
        self.create_widgets()

    def create_menu_bar(self):
        """Create professional menu bar"""
        menubar = tk.Menu(self.root, bg="#3c3c3c", fg="white", activebackground="#4a4a4a", activeforeground="white")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#3c3c3c", fg="white", activebackground="#4a4a4a", activeforeground="white")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File...", command=self.select_file)
        file_menu.add_command(label="Add to Queue...", command=self.add_to_queue)
        file_menu.add_separator()
        file_menu.add_command(label="Save Settings", command=self.save_settings)
        file_menu.add_command(label="Load Settings", command=self.load_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg="#3c3c3c", fg="white", activebackground="#4a4a4a", activeforeground="white")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Queue", command=self.clear_queue)
        edit_menu.add_command(label="Remove Selected", command=self.remove_selected_file)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#3c3c3c", fg="white", activebackground="#4a4a4a", activeforeground="white")
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Preview Video", command=self.preview_video)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg="#3c3c3c", fg="white", activebackground="#4a4a4a", activeforeground="white")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Generate Video", command=self.generate_video)
        tools_menu.add_command(label="Process Queue", command=self.process_queue)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#3c3c3c", fg="white", activebackground="#4a4a4a", activeforeground="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_widgets(self):
        # Main container with dark theme
        main_container = tk.Frame(self.root, bg="#2b2b2b")
        main_container.pack(fill="both", expand=True)
        
        # Create paned windows for professional layout
        main_paned = tk.PanedWindow(main_container, orient="horizontal", bg="#2b2b2b", sashwidth=3, sashrelief="raised")
        main_paned.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Left panel - Data Explorer
        left_panel = tk.Frame(main_paned, bg="#3c3c3c", width=350)
        main_paned.add(left_panel, minsize=300)
        
        # Right panel - Main workspace
        right_panel = tk.Frame(main_paned, bg="#2b2b2b")
        main_paned.add(right_panel, minsize=800)
        
        # Create left panel content
        self.create_data_explorer(left_panel)
        
        # Create right panel content
        self.create_main_workspace(right_panel)

    def create_data_explorer(self, parent):
        """Create the left data explorer panel"""
        # Data Explorer header
        header_frame = tk.Frame(parent, bg="#4a4a4a", height=40)
        header_frame.pack(fill="x", pady=(0, 2))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Data Explorer", font=("Arial", 12, "bold"), 
                              bg="#4a4a4a", fg="white")
        title_label.pack(side="left", padx=10, pady=10)
        
        # Refresh and collapse buttons
        refresh_btn = tk.Button(header_frame, text="↻", font=("Arial", 10), width=3,
                               bg="#5a5a5a", fg="white", relief="flat", command=self.refresh_file_list)
        refresh_btn.pack(side="right", padx=5, pady=8)
        
        collapse_btn = tk.Button(header_frame, text="−", font=("Arial", 10), width=3,
                                bg="#5a5a5a", fg="white", relief="flat")
        collapse_btn.pack(side="right", padx=5, pady=8)
        
        # Filter bar
        filter_frame = tk.Frame(parent, bg="#3c3c3c", height=30)
        filter_frame.pack(fill="x", pady=(0, 2))
        filter_frame.pack_propagate(False)
        
        filter_label = tk.Label(filter_frame, text="Filter:", bg="#3c3c3c", fg="#cccccc", font=("Arial", 9))
        filter_label.pack(side="left", padx=10, pady=5)
        
        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(filter_frame, textvariable=self.filter_var, bg="#2b2b2b", fg="white",
                                    insertbackground="white", relief="flat", font=("Arial", 9))
        self.filter_entry.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=5)
        
        # File tree with scrollbar
        tree_frame = tk.Frame(parent, bg="#3c3c3c")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Scrollbar for file tree
        tree_scrollbar = tk.Scrollbar(tree_frame, bg="#3c3c3c")
        tree_scrollbar.pack(side="right", fill="y")
        
        # File listbox styled like a tree
        self.file_listbox = tk.Listbox(tree_frame, yscrollcommand=tree_scrollbar.set, 
                                      bg="#2b2b2b", fg="#cccccc", selectbackground="#4a4a4a",
                                      selectforeground="white", font=("Consolas", 9), relief="flat",
                                      borderwidth=0, highlightthickness=0)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        tree_scrollbar.config(command=self.file_listbox.yview)
        
        # File list context menu
        self.file_context_menu = tk.Menu(self.root, tearoff=0, bg="#3c3c3c", fg="white",
                                        activebackground="#4a4a4a", activeforeground="white")
        self.file_context_menu.add_command(label="Remove from Queue", command=self.remove_selected_file)
        self.file_listbox.bind("<Button-3>", self.show_file_context_menu)
        
        # Queue controls
        controls_frame = tk.Frame(parent, bg="#3c3c3c", height=60)
        controls_frame.pack(fill="x", pady=(2, 0))
        controls_frame.pack_propagate(False)
        
        self.clear_queue_btn = tk.Button(controls_frame, text="Clear All", command=self.clear_queue,
                                        bg="#5a5a5a", fg="white", relief="flat", font=("Arial", 9))
        self.clear_queue_btn.pack(side="left", padx=5, pady=10)
        
        self.remove_selected_btn = tk.Button(controls_frame, text="Remove Selected", command=self.remove_selected_file,
                                           bg="#5a5a5a", fg="white", relief="flat", font=("Arial", 9))
        self.remove_selected_btn.pack(side="left", padx=5, pady=10)

    def create_main_workspace(self, parent):
        """Create the main workspace panel"""
        # Create vertical paned window for main workspace
        workspace_paned = tk.PanedWindow(parent, orient="vertical", bg="#2b2b2b", sashwidth=3, sashrelief="raised")
        workspace_paned.pack(fill="both", expand=True)
        
        # Top panel - File processing and settings
        top_panel = tk.Frame(workspace_paned, bg="#3c3c3c", height=400)
        workspace_paned.add(top_panel, minsize=300)
        
        # Bottom panel - Results and preview
        bottom_panel = tk.Frame(workspace_paned, bg="#2b2b2b")
        workspace_paned.add(bottom_panel, minsize=200)
        
        # Create top panel content
        self.create_processing_panel(top_panel)
        
        # Create bottom panel content
        self.create_results_panel(bottom_panel)

    def create_processing_panel(self, parent):
        """Create the file processing and settings panel"""
        # File upload section
        upload_frame = tk.LabelFrame(parent, text="File Processing", font=("Arial", 11, "bold"),
                                    bg="#3c3c3c", fg="white", relief="flat", bd=1)
        upload_frame.pack(fill="x", padx=10, pady=10)
        
        # File selection
        file_frame = tk.Frame(upload_frame, bg="#3c3c3c")
        file_frame.pack(fill="x", padx=10, pady=10)
        
        self.select_file_btn = tk.Button(file_frame, text="Select File", command=self.select_file,
                                        bg="#5a5a5a", fg="white", relief="flat", font=("Arial", 10))
        self.select_file_btn.pack(side="left", padx=(0, 10))
        
        self.file_label = tk.Label(file_frame, text="No file selected", fg="#cccccc", 
                                  font=("Arial", 9), bg="#3c3c3c")
        self.file_label.pack(side="left")
        
        # File type detection
        self.file_type_label = tk.Label(upload_frame, text="", fg="#4CAF50", font=("Arial", 9), bg="#3c3c3c")
        self.file_type_label.pack(pady=(0, 10))
        
        # Batch processing
        batch_frame = tk.Frame(upload_frame, bg="#3c3c3c")
        batch_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.add_to_queue_btn = tk.Button(batch_frame, text="Add to Queue", command=self.add_to_queue,
                                         bg="#5a5a5a", fg="white", relief="flat", font=("Arial", 9))
        self.add_to_queue_btn.pack(side="left", padx=(0, 10))
        
        self.queue_label = tk.Label(batch_frame, text="Queue: 0 files", fg="#4CAF50", font=("Arial", 9), bg="#3c3c3c")
        self.queue_label.pack(side="left")
        
        # Settings panels in horizontal layout
        settings_container = tk.Frame(parent, bg="#3c3c3c")
        settings_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left settings column
        left_settings = tk.Frame(settings_container, bg="#3c3c3c")
        left_settings.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Right settings column
        right_settings = tk.Frame(settings_container, bg="#3c3c3c")
        right_settings.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Create settings panels
        self.create_text_settings(left_settings)
        self.create_window_settings(right_settings)

    def create_text_settings(self, parent):
        """Create text settings panel"""
        text_frame = tk.LabelFrame(parent, text="Text Settings", font=("Arial", 10, "bold"),
                                  bg="#3c3c3c", fg="white", relief="flat", bd=1)
        text_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Font family
        font_family_frame = tk.Frame(text_frame, bg="#3c3c3c")
        font_family_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(font_family_frame, text="Font Family:", bg="#3c3c3c", fg="#cccccc", font=("Arial", 9)).pack(side="left")
        self.font_family_var = tk.StringVar(value="Arial")
        self.font_family_combo = ttk.Combobox(font_family_frame, textvariable=self.font_family_var,
                                             values=["Arial", "Times New Roman", "Courier New", "Helvetica"],
                                             state="readonly", width=15)
        self.font_family_combo.pack(side="right")
        
        # Font size
        font_size_frame = tk.Frame(text_frame, bg="#3c3c3c")
        font_size_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(font_size_frame, text="Font Size:", bg="#3c3c3c", fg="#cccccc", font=("Arial", 9)).pack(side="left")
        self.font_size_var = tk.IntVar(value=30)
        self.font_size_entry = tk.Entry(font_size_frame, textvariable=self.font_size_var, width=10,
                                       bg="#2b2b2b", fg="white", insertbackground="white", relief="flat")
        self.font_size_entry.pack(side="right")
        
        # Bold checkbox
        self.bold_var = tk.BooleanVar(value=True)
        self.bold_check = tk.Checkbutton(text_frame, text="Bold", variable=self.bold_var,
                                        bg="#3c3c3c", fg="#cccccc", selectcolor="#2b2b2b",
                                        activebackground="#3c3c3c", activeforeground="#cccccc",
                                        font=("Arial", 9))
        self.bold_check.pack(anchor="w", padx=10, pady=5)
        
        # Margin
        margin_frame = tk.Frame(text_frame, bg="#3c3c3c")
        margin_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(margin_frame, text="Margin:", bg="#3c3c3c", fg="#cccccc", font=("Arial", 9)).pack(side="left")
        self.margin_var = tk.IntVar(value=20)
        self.margin_entry = tk.Entry(margin_frame, textvariable=self.margin_var, width=10,
                                    bg="#2b2b2b", fg="white", insertbackground="white", relief="flat")
        self.margin_entry.pack(side="right")

    def create_window_settings(self, parent):
        """Create moving window settings panel"""
        window_frame = tk.LabelFrame(parent, text="Moving Window", font=("Arial", 10, "bold"),
                                    bg="#3c3c3c", fg="white", relief="flat", bd=1)
        window_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Enable moving window
        self.moving_window_var = tk.BooleanVar(value=False)
        self.moving_window_check = tk.Checkbutton(window_frame, text="Enable Moving Window",
                                                 variable=self.moving_window_var, command=self.update_window_controls,
                                                 bg="#3c3c3c", fg="#cccccc", selectcolor="#2b2b2b",
                                                 activebackground="#3c3c3c", activeforeground="#cccccc",
                                                 font=("Arial", 9))
        self.moving_window_check.pack(anchor="w", padx=10, pady=5)
        
        # Window size
        window_size_frame = tk.Frame(window_frame, bg="#3c3c3c")
        window_size_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(window_size_frame, text="Window Size:", bg="#3c3c3c", fg="#cccccc", font=("Arial", 9)).pack(side="left")
        self.window_size_var = tk.IntVar(value=10)
        self.window_size_entry = tk.Entry(window_size_frame, textvariable=self.window_size_var, width=10,
                                         bg="#2b2b2b", fg="white", insertbackground="white", relief="flat")
        self.window_size_entry.pack(side="right")
        
        # Mask character
        mask_frame = tk.Frame(window_frame, bg="#3c3c3c")
        mask_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(mask_frame, text="Mask Character:", bg="#3c3c3c", fg="#cccccc", font=("Arial", 9)).pack(side="left")
        self.mask_character_var = tk.StringVar(value="_")
        self.mask_character_entry = tk.Entry(mask_frame, textvariable=self.mask_character_var, width=10,
                                           bg="#2b2b2b", fg="white", insertbackground="white", relief="flat")
        self.mask_character_entry.pack(side="right")
        
        # Speed settings
        speed_frame = tk.LabelFrame(parent, text="Speed Settings", font=("Arial", 10, "bold"),
                                   bg="#3c3c3c", fg="white", relief="flat", bd=1)
        speed_frame.pack(fill="x", pady=(0, 10))
        
        # Speed multiplier
        speed_mult_frame = tk.Frame(speed_frame, bg="#3c3c3c")
        speed_mult_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(speed_mult_frame, text="Speed Multiplier:", bg="#3c3c3c", fg="#cccccc", font=("Arial", 9)).pack(side="left")
        self.speed_multiplier_var = tk.DoubleVar(value=1.0)
        self.speed_multiplier_entry = tk.Entry(speed_mult_frame, textvariable=self.speed_multiplier_var, width=10,
                                              bg="#2b2b2b", fg="white", insertbackground="white", relief="flat")
        self.speed_multiplier_entry.pack(side="right")
        
        # Action buttons
        action_frame = tk.Frame(parent, bg="#3c3c3c")
        action_frame.pack(fill="x", pady=10)
        
        self.generate_btn = tk.Button(action_frame, text="Generate Video", command=self.generate_video,
                                     state=tk.DISABLED, bg="#4CAF50", fg="white", relief="flat",
                                     font=("Arial", 10, "bold"))
        self.generate_btn.pack(side="left", padx=(0, 10))
        
        self.batch_generate_btn = tk.Button(action_frame, text="Process Queue", command=self.process_queue,
                                           bg="#2196F3", fg="white", relief="flat", font=("Arial", 10, "bold"))
        self.batch_generate_btn.pack(side="left", padx=(0, 10))
        
        self.preview_btn = tk.Button(action_frame, text="Preview", command=self.preview_video,
                                    bg="#FF9800", fg="white", relief="flat", font=("Arial", 10))
        self.preview_btn.pack(side="left", padx=(0, 10))
        
        self.save_settings_btn = tk.Button(action_frame, text="Save Settings", command=self.save_settings,
                                          bg="#5a5a5a", fg="white", relief="flat", font=("Arial", 10))
        self.save_settings_btn.pack(side="right")

    def create_results_panel(self, parent):
        """Create the results and preview panel"""
        # Results header
        results_header = tk.Frame(parent, bg="#4a4a4a", height=40)
        results_header.pack(fill="x", pady=(0, 2))
        results_header.pack_propagate(False)
        
        results_title = tk.Label(results_header, text="Processing Results", font=("Arial", 12, "bold"),
                                bg="#4a4a4a", fg="white")
        results_title.pack(side="left", padx=10, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(parent, mode="determinate", style="Custom.Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=10, pady=10)
        self.progress.pack_forget()
        
        # Status label
        self.status_label = tk.Label(parent, text="Ready", fg="#4CAF50", font=("Arial", 10), bg="#2b2b2b")
        self.status_label.pack(pady=10)
        
        # Results text area
        results_frame = tk.Frame(parent, bg="#2b2b2b")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Text widget for results
        self.results_text = tk.Text(results_frame, bg="#1e1e1e", fg="#cccccc", font=("Consolas", 9),
                                   insertbackground="white", selectbackground="#4a4a4a", relief="flat",
                                   borderwidth=0, wrap="word")
        self.results_text.pack(fill="both", expand=True)
        
        # Scrollbar for results
        results_scrollbar = tk.Scrollbar(results_frame, command=self.results_text.yview)
        results_scrollbar.pack(side="right", fill="y")
        self.results_text.config(yscrollcommand=results_scrollbar.set)

    def refresh_file_list(self):
        """Refresh the file list display"""
        self.update_queue_display()

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Typing Analysis Workstation 1.0\n\nProfessional tool for analyzing typing patterns and generating video visualizations from XML, IDFX, and text files.")

    def update_window_controls(self):
        """Update moving window controls based on checkbox state"""
        state = "normal" if self.moving_window_var.get() else "disabled"
        self.window_size_entry.config(state=state)
        self.mask_character_entry.config(state=state)

        # Initialize file tracking variables
        self.current_file_path = None
        self.current_file_type = None

        # Load settings if available
        self.load_settings()

    def select_file(self):
        """Select a file and automatically detect its type"""
        path = filedialog.askopenfilename(filetypes=[
            ("All Supported Files", "*.xml *.docx *.txt *.idfx"),
            ("XML Files", "*.xml"),
            ("Word Files", "*.docx"),
            ("Text Files", "*.txt"),
            ("IDFX Files", "*.idfx"),
            ("All Files", "*.*")
        ])
        
        if path:
            self.current_file_path = path
            file_type = self.detect_file_type(path)
            self.current_file_type = file_type
            
            # Update UI
            self.file_label.config(text=f"Selected: {os.path.basename(path)}", fg="black")
            self.file_type_label.config(text=f"File Type: {file_type.upper()}", fg="blue")
            self.generate_btn.config(state=tk.NORMAL)
            
            messagebox.showinfo("File Selected", f"Selected {file_type.upper()} file: {os.path.basename(path)}")

    def detect_file_type(self, file_path):
        """Detect file type based on extension and content"""
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.xml':
            # Check if it's an IDFX file by looking at content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Read first 1000 characters
                    if 'idfx' in content.lower() or 'typing' in content.lower():
                        return 'idfx'
                    else:
                        return 'xml'
            except:
                return 'xml'
        elif ext == '.docx':
            return 'word'
        elif ext == '.txt':
            return 'txt'
        elif ext == '.idfx':
            return 'idfx'
        else:
            # Try to detect by content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)
                    if 'idfx' in content.lower() or 'typing' in content.lower():
                        return 'idfx'
                    elif '<' in content and '>' in content:
                        return 'xml'
                    else:
                        return 'txt'
            except:
                return 'txt'

    def add_to_queue(self):
        """Add files to the unified queue"""
        paths = filedialog.askopenfilenames(filetypes=[
            ("All Supported Files", "*.xml *.docx *.txt *.idfx"),
            ("XML Files", "*.xml"),
            ("Word Files", "*.docx"),
            ("Text Files", "*.txt"),
            ("IDFX Files", "*.idfx"),
            ("All Files", "*.*")
        ])
        
        if paths:
            added_count = 0
            for path in paths:
                file_type = self.detect_file_type(path)
                if path not in [item['path'] for item in self.file_queue]:
                    self.file_queue.append({
                        'path': path,
                        'type': file_type
                    })
                    added_count += 1
            
            self.update_queue_display()
            messagebox.showinfo("Files Added", f"Added {added_count} file(s) to queue")

    def clear_queue(self):
        """Clear the unified file queue"""
        self.file_queue = []
        self.update_queue_display()
        messagebox.showinfo("Queue Cleared", "File queue has been cleared")

    def update_queue_display(self):
        """Update the queue display in both sidebar and main area"""
        count = len(self.file_queue)
        self.queue_label.config(text=f"Queue: {count} files")
        
        # Update sidebar file list
        self.file_listbox.delete(0, tk.END)
        for i, file_item in enumerate(self.file_queue):
            filename = os.path.basename(file_item['path'])
            file_type = file_item['type'].upper()
            display_text = f"{i+1}. [{file_type}] {filename}"
            self.file_listbox.insert(tk.END, display_text)
        
        if count > 0:
            # Show file types in queue
            types = [item['type'].upper() for item in self.file_queue]
            type_counts = {}
            for file_type in types:
                type_counts[file_type] = type_counts.get(file_type, 0) + 1
            
            type_summary = ", ".join([f"{count} {type}" for type, count in type_counts.items()])
            self.queue_label.config(text=f"Queue: {count} files ({type_summary})")

    def remove_selected_file(self):
        """Remove the selected file from the queue"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.file_queue):
                removed_file = self.file_queue.pop(index)
                self.update_queue_display()
                messagebox.showinfo("File Removed", f"Removed: {os.path.basename(removed_file['path'])}")

    def show_file_context_menu(self, event):
        """Show context menu for file list"""
        try:
            self.file_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.file_context_menu.grab_release()

    def update_xml_queue_display(self):
        count = len(self.xml_queue)
        self.xml_queue_label.config(text=f"Queue: {count} files")
        if count > 0:
            self.batch_generate_btn.config(state=tk.NORMAL)
        else:
            self.batch_generate_btn.config(state=tk.DISABLED)

    def update_data_queue_display(self):
        count = len(self.data_queue)
        self.data_queue_label.config(text=f"Queue: {count} files")
        if count > 0:
            self.batch_generate_data_btn.config(state=tk.NORMAL)
        else:
            self.batch_generate_data_btn.config(state=tk.DISABLED)

    def update_idfx_queue_display(self):
        count = len(getattr(self, 'idfx_queue', []))
        self.idfx_queue_label.config(text=f"Queue: {count} files")
        if count > 0:
            self.batch_generate_idfx_btn.config(state=tk.NORMAL)
        else:
            self.batch_generate_idfx_btn.config(state=tk.DISABLED)

    def process_xml_queue(self):
        if not self.xml_queue:
            messagebox.showwarning("Warning", "No files in queue")
            return
        
        if self.processing:
            messagebox.showwarning("Warning", "Already processing files")
            return
        
        self.processing = True
        self.batch_generate_btn.config(state=tk.DISABLED)
        self.progress_xml.pack(pady=5, fill="x", padx=10)
        self.progress_xml.config(maximum=len(self.xml_queue), value=0)
        
        def process_queue():
            try:
                # Create output folder in the program directory
                program_dir = os.path.dirname(os.path.abspath(__file__))
                output_folder = os.path.join(program_dir, 'xml-to-text-video-output')
                os.makedirs(output_folder, exist_ok=True)
                
                for i, item in enumerate(self.xml_queue):
                    try:
                        xml_path = item['xml_path']
                        word_path = item['word_path']
                        
                        # Update status
                        filename = os.path.basename(xml_path)
                        self.xml_status_label.config(text=f"Processing: {filename}", fg="blue")
                        self.root.update_idletasks()
                        
                        # Simulate individual processing by temporarily setting the paths
                        original_xml_path = self.xml_path
                        original_word_path = self.word_path
                        
                        self.xml_path = xml_path
                        self.word_path = word_path
                        
                        # Use the existing generate_video logic
                        events = self.parse_xml_events(xml_path)
                        settings = self.get_settings()
                        
                        # Load settings from file (if exists) and use for video generation
                        # Load settings from program directory
                        program_dir = os.path.dirname(os.path.abspath(__file__))
                        settings_path = os.path.join(program_dir, 'xml-to-text-settings.json')
                        if os.path.exists(settings_path):
                            with open(settings_path, 'r') as f:
                                settings = json.load(f)
                        else:
                            settings = self.get_settings()
                        
                        # Reconstruct text as it grows (uses speed settings)
                        text_states, frame_times = self.reconstruct_text_states(events, settings)
                        
                        # Get font settings from settings
                        font_family = settings["font_family"]
                        font_size = settings["font_size"]
                        bold = settings["bold"]
                        
                        # Generate frames with font settings from JSON
                        frames = self.generate_frames(
                            text_states, frame_times, font_family, font_size, bold,
                            settings.get("moving_window", False),
                            settings.get("window_size", 10),
                            settings.get("window_wordonly", False),
                            settings.get("mask_character", "_"),
                            settings.get("margin", 20)
                        )
                        
                        # Assemble video
                        if settings["save_video"]:
                            xml_filename = os.path.splitext(os.path.basename(xml_path))[0]
                            output_path = os.path.join(output_folder, f'{xml_filename}.mp4')
                            self.save_video(frames, frame_times, output_path)
                        
                        # Restore original paths
                        self.xml_path = original_xml_path
                        self.word_path = original_word_path
                        
                        # Update progress
                        self.progress_xml.config(value=i + 1)
                        self.root.update_idletasks()
                        
                    except Exception as e:
                        error_msg = f"Failed to process {os.path.basename(xml_path)}: {str(e)}"
                        print(f"DEBUG: {error_msg}")
                        messagebox.showerror("Error", error_msg)
                
                self.xml_status_label.config(text=f"Batch processing complete! Videos saved to {output_folder}", fg="green")
                messagebox.showinfo("Complete", f"Processed {len(self.xml_queue)} files. Videos saved to {output_folder}")
                
            except Exception as e:
                error_msg = f"Batch processing failed: {str(e)}"
                print(f"DEBUG: {error_msg}")
                self.xml_status_label.config(text=error_msg, fg="red")
                messagebox.showerror("Error", error_msg)
            finally:
                self.processing = False
                self.batch_generate_btn.config(state=tk.NORMAL)
                self.progress_xml.pack_forget()
                self.xml_status_label.config(text="")
        
        threading.Thread(target=process_queue, daemon=True).start()

    def process_data_queue(self):
        if not self.data_queue:
            messagebox.showwarning("Warning", "No files in queue")
            return
        
        if self.processing:
            messagebox.showwarning("Warning", "Already processing files")
            return
        
        self.processing = True
        self.batch_generate_data_btn.config(state=tk.DISABLED)
        self.progress_data.pack(pady=5, fill="x", padx=10)
        self.progress_data.config(maximum=len(self.data_queue), value=0)
        
        def process_queue():
            try:
                # Create output folder in the program directory
                program_dir = os.path.dirname(os.path.abspath(__file__))
                output_folder = os.path.join(program_dir, 'xml-to-text-video-output')
                os.makedirs(output_folder, exist_ok=True)
                
                for i, item in enumerate(self.data_queue):
                    try:
                        data_path = item['data_path']
                        
                        # Update status
                        filename = os.path.basename(data_path)
                        self.data_status_label.config(text=f"Processing: {filename}", fg="blue")
                        self.root.update_idletasks()
                        
                        # Simulate individual processing by temporarily setting the path
                        original_data_path = getattr(self, 'data_txt_path', None)
                        self.data_txt_path = data_path
                        
                        # Use the existing generate_video_from_data_txt logic
                        events = self.parse_data_txt_events(data_path)
                        settings = self.get_settings()
                        
                        # Load settings from file (if exists) and use for video generation
                        # Load settings from program directory
                        program_dir = os.path.dirname(os.path.abspath(__file__))
                        settings_path = os.path.join(program_dir, 'xml-to-text-settings.json')
                        if os.path.exists(settings_path):
                            with open(settings_path, 'r') as f:
                                settings = json.load(f)
                        else:
                            settings = self.get_settings()
                        
                        text_states, frame_times = self.reconstruct_data_txt_text_states(events, settings)
                        
                        if not text_states or not frame_times:
                            continue
                        
                        # Get font settings from settings
                        font_family = settings["font_family"]
                        font_size = settings["font_size"]
                        bold = settings["bold"]
                        
                        # Generate frames with font settings from JSON
                        frames = self.generate_frames(
                            text_states, frame_times, font_family, font_size, bold,
                            settings.get("moving_window", False),
                            settings.get("window_size", 10),
                            settings.get("window_wordonly", False),
                            settings.get("mask_character", "_"),
                            settings.get("margin", 20)
                        )
                        
                        # Save video
                        data_filename = os.path.splitext(os.path.basename(data_path))[0]
                        output_path = os.path.join(output_folder, f'{data_filename}_data.mp4')
                        self.save_video(frames, frame_times, output_path)
                        
                        # Restore original path
                        self.data_txt_path = original_data_path
                        
                        # Update progress
                        self.progress_data.config(value=i + 1)
                        self.root.update_idletasks()
                        
                    except Exception as e:
                        error_msg = f"Failed to process {os.path.basename(data_path)}: {str(e)}"
                        print(f"DEBUG: {error_msg}")
                        messagebox.showerror("Error", error_msg)
                
                self.data_status_label.config(text=f"Batch processing complete! Videos saved to {output_folder}", fg="green")
                messagebox.showinfo("Complete", f"Processed {len(self.data_queue)} files. Videos saved to {output_folder}")
                
            except Exception as e:
                error_msg = f"Batch processing failed: {str(e)}"
                print(f"DEBUG: {error_msg}")
                self.data_status_label.config(text=error_msg, fg="red")
                messagebox.showerror("Error", error_msg)
            finally:
                self.processing = False
                self.batch_generate_data_btn.config(state=tk.NORMAL)
                self.progress_data.pack_forget()
                self.data_status_label.config(text="")
        
        threading.Thread(target=process_queue, daemon=True).start()

    def process_idfx_queue(self):
        if not getattr(self, 'idfx_queue', []):
            messagebox.showwarning("Warning", "No files in queue")
            return
        if self.processing:
            messagebox.showwarning("Warning", "Already processing files")
            return
        self.processing = True
        self.batch_generate_idfx_btn.config(state=tk.DISABLED)
        self.progress_idfx.pack(pady=5, fill="x", padx=10)
        self.progress_idfx.config(maximum=len(self.idfx_queue), value=0)
        def process_queue():
            try:
                # Create output folder in the program directory
                program_dir = os.path.dirname(os.path.abspath(__file__))
                output_folder = os.path.join(program_dir, 'xml-to-text-video-output')
                os.makedirs(output_folder, exist_ok=True)
                for i, item in enumerate(self.idfx_queue):
                    try:
                        idfx_path = item['idfx_path']
                        filename = os.path.basename(idfx_path)
                        self.idfx_status_label.config(text=f"Processing: {filename}", fg="blue")
                        self.root.update_idletasks()
                        events = self.parse_idfx_events(idfx_path)
                        settings = self.get_settings()
                        text_states, frame_times = self.reconstruct_idfx_text_states(events, settings)
                        if not text_states or not frame_times:
                            continue
                        font_family = settings["font_family"]
                        font_size = settings["font_size"]
                        bold = settings["bold"]
                        frames = self.generate_frames(
                            text_states, frame_times, font_family, font_size, bold,
                            settings.get("moving_window", False),
                            settings.get("window_size", 10),
                            settings.get("window_wordonly", False),
                            settings.get("mask_character", "_"),
                            settings.get("margin", 20)
                        )
                        idfx_filename = os.path.splitext(os.path.basename(idfx_path))[0]
                        output_path = os.path.join(output_folder, f'{idfx_filename}_idfx.mp4')
                        self.save_video(frames, frame_times, output_path)
                        self.progress_idfx.config(value=i + 1)
                        self.root.update_idletasks()
                    except Exception as e:
                        error_msg = f"Failed to process {os.path.basename(idfx_path)}: {str(e)}"
                        print(f"DEBUG: {error_msg}")
                        messagebox.showerror("Error", error_msg)
                self.idfx_status_label.config(text=f"Batch processing complete! Videos saved to {output_folder}", fg="green")
                messagebox.showinfo("Complete", f"Processed {len(self.idfx_queue)} files. Videos saved to {output_folder}")
            except Exception as e:
                error_msg = f"Batch processing failed: {str(e)}"
                print(f"DEBUG: {error_msg}")
                self.idfx_status_label.config(text=error_msg, fg="red")
                messagebox.showerror("Error", error_msg)
            finally:
                self.processing = False
                self.batch_generate_idfx_btn.config(state=tk.NORMAL)
                self.progress_idfx.pack_forget()
                self.idfx_status_label.config(text="")
        threading.Thread(target=process_queue, daemon=True).start()

    def check_ready(self):
        if self.xml_path and self.word_path:
            self.generate_btn.config(state=tk.NORMAL)

    def generate_video(self):
        if not self.current_file_path or not self.current_file_type:
            messagebox.showerror("Error", "Please select a file first")
            return

        self.processing = True
        self.generate_btn.config(state=tk.DISABLED)
        self.progress.pack()
        self.status_label.config(text="Generating video...")

        def generate():
            try:
                # Route to appropriate generation method based on file type
                if self.current_file_type == 'xml':
                    self.generate_xml_video()
                elif self.current_file_type == 'word':
                    self.generate_word_video()
                elif self.current_file_type == 'txt':
                    self.generate_txt_video()
                elif self.current_file_type == 'idfx':
                    self.generate_idfx_video()
        else:
                    raise ValueError(f"Unsupported file type: {self.current_file_type}")

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate video: {str(e)}"))
            finally:
                self.root.after(0, self.reset_ui)

        threading.Thread(target=generate, daemon=True).start()

    def generate_xml_video(self):
        """Generate video from XML file"""
        try:
            # Load settings
            program_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(program_dir, 'xml-to-text-settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            else:
                settings = self.get_settings()
            
            # Parse XML and reconstruct typing sequence
            events = self.parse_xml_events(self.current_file_path)
            text_states, frame_times = self.reconstruct_text_states(events, settings)
            
            # Generate frames
            frames = self.generate_frames(
                text_states, frame_times, 
                settings.get("font_family", "Arial"),
                settings.get("font_size", 30),
                settings.get("bold", True),
                settings.get("moving_window", False),
                settings.get("window_size", 10),
                settings.get("window_wordonly", False),
                settings.get("mask_character", "_"),
                settings.get("margin", 20)
            )
            
            # Save video
            if settings.get("save_video", True):
                output_folder = os.path.join(program_dir, 'xml-to-text-video-output')
                os.makedirs(output_folder, exist_ok=True)
                filename = os.path.splitext(os.path.basename(self.current_file_path))[0]
                output_path = os.path.join(output_folder, f'{filename}.mp4')
                self.save_video(frames, frame_times, output_path)
                self.root.after(0, lambda: messagebox.showinfo("Success", f"XML video saved to: {output_path}"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Success", "XML video generated successfully (not saved)"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate XML video: {str(e)}"))

    def generate_word_video(self):
        """Generate video from Word file"""
        self.root.after(0, lambda: messagebox.showinfo("Success", f"Word video generated from: {os.path.basename(self.current_file_path)}"))

    def generate_txt_video(self):
        """Generate video from text file"""
        try:
            # Load settings
                program_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(program_dir, 'xml-to-text-settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            else:
                settings = self.get_settings()
            
            # Read text file and create text states
            with open(self.current_file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            
            # Create text states and frame times
            text_states, frame_times = self.reconstruct_data_txt_text_states(text, settings)
            
            # Generate frames
            frames = self.generate_frames(
                text_states, frame_times, 
                settings.get("font_family", "Arial"),
                settings.get("font_size", 30),
                settings.get("bold", True),
                settings.get("moving_window", False),
                settings.get("window_size", 10),
                settings.get("window_wordonly", False),
                settings.get("mask_character", "_"),
                settings.get("margin", 20)
            )
            
            # Save video
            if settings.get("save_video", True):
                output_folder = os.path.join(program_dir, 'xml-to-text-video-output')
                os.makedirs(output_folder, exist_ok=True)
                filename = os.path.splitext(os.path.basename(self.current_file_path))[0]
                output_path = os.path.join(output_folder, f'{filename}.mp4')
                self.save_video(frames, frame_times, output_path)
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Text video saved to: {output_path}"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Text video generated successfully (not saved)"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate text video: {str(e)}"))

    def generate_idfx_video(self):
        """Generate video from IDFX file"""
        try:
            # Load settings
            program_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(program_dir, 'xml-to-text-settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            else:
                settings = self.get_settings()
            
            # Parse IDFX events
            events = self.parse_idfx_events(self.current_file_path)
            text_states, frame_times = self.reconstruct_idfx_text_states(events, settings)
            
            # Generate frames
            frames = self.generate_frames(
                text_states, frame_times, 
                settings.get("font_family", "Arial"),
                settings.get("font_size", 30),
                settings.get("bold", True),
                settings.get("moving_window", False),
                settings.get("window_size", 10),
                settings.get("window_wordonly", False),
                settings.get("mask_character", "_"),
                settings.get("margin", 20)
            )
            
            # Save video
            if settings.get("save_video", True):
                output_folder = os.path.join(program_dir, 'xml-to-text-video-output')
                os.makedirs(output_folder, exist_ok=True)
                filename = os.path.splitext(os.path.basename(self.current_file_path))[0]
                output_path = os.path.join(output_folder, f'{filename}.mp4')
                self.save_video(frames, frame_times, output_path)
                self.root.after(0, lambda: messagebox.showinfo("Success", f"IDFX video saved to: {output_path}"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Success", "IDFX video generated successfully (not saved)"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate IDFX video: {str(e)}"))

    def process_queue(self):
        """Process all files in the queue"""
        if not self.file_queue:
            messagebox.showwarning("Warning", "No files in queue")
            return

        self.processing = True
        self.batch_generate_btn.config(state=tk.DISABLED)
        self.progress.pack()
        self.status_label.config(text="Processing queue...")

        def process():
            try:
                total_files = len(self.file_queue)
                for i, file_item in enumerate(self.file_queue):
                    self.current_file_path = file_item['path']
                    self.current_file_type = file_item['type']
                    
                    # Update progress
                    progress = (i / total_files) * 100
                    self.root.after(0, lambda p=progress: self.progress.config(value=p))
                    self.root.after(0, lambda: self.status_label.config(text=f"Processing {i+1}/{total_files}: {os.path.basename(self.current_file_path)}"))
                    
                    # Generate video based on file type
                    if self.current_file_type == 'xml':
                        self.generate_xml_video()
                    elif self.current_file_type == 'word':
                        self.generate_word_video()
                    elif self.current_file_type == 'txt':
                        self.generate_txt_video()
                    elif self.current_file_type == 'idfx':
                        self.generate_idfx_video()
                
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Processed {total_files} files successfully"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to process queue: {str(e)}"))
            finally:
                self.root.after(0, self.reset_ui)

        threading.Thread(target=process, daemon=True).start()

    def reset_ui(self):
        """Reset UI after processing"""
        self.processing = False
        self.generate_btn.config(state=tk.NORMAL)
        self.batch_generate_btn.config(state=tk.NORMAL)
        self.progress.pack_forget()
        self.status_label.config(text="")

    def generate_video_from_data_txt(self):
        if not hasattr(self, 'data_txt_path') or not self.data_txt_path:
            messagebox.showerror("Error", "No data.txt file selected.")
            return
        self.status_label = getattr(self, 'status_label', None)
        if not self.status_label:
            self.status_label = tk.Label(self.tab2, text="Generating video, please wait...", fg="blue")
            self.status_label.pack(pady=5)
        else:
            self.status_label.config(text="Generating video, please wait...", fg="blue")
        self.root.update_idletasks()
        self.progress_data.pack(pady=5, fill="x", padx=10)
        self.progress_data.start()

        def do_generate():
            try:
                self.status_label.config(text="Parsing data.txt...", fg="blue")
                print("[DEBUG] Starting to parse data.txt events...")
                events = self.parse_data_txt_events(self.data_txt_path)
                print(f"[DEBUG] Parsed {len(events)} events from data.txt.")
                self.status_label.config(text=f"Parsed {len(events)} events. Reconstructing text states...", fg="blue")
                settings = self.get_settings()
                text_states, frame_times = self.reconstruct_data_txt_text_states(events, settings)
                print(f"[DEBUG] Reconstructed {len(text_states)} text states.")
                self.status_label.config(text=f"Reconstructed {len(text_states)} text states. Generating frames...", fg="blue")
                if not text_states or not frame_times or len(text_states) != len(frame_times):
                    self.status_label.config(text="Error: No valid typing events found in file or data is malformed.", fg="red")
                    messagebox.showerror("Error", "No valid typing events found in file or data is malformed.")
                    self.progress_data.stop()
                    self.progress_data.pack_forget()
                    return
                font_family = settings["font_family"]
                font_size = settings["font_size"]
                bold = settings["bold"]
                print("[DEBUG] Generating frames...")
                def update_progress(current, total):
                    self.status_label.config(text=f"Generating frames: {current}/{total}", fg="blue")
                frames = self.generate_frames(
                    text_states, frame_times, font_family, font_size, bold,
                    settings.get("moving_window", False),
                    settings.get("window_size", 10),
                    settings.get("window_wordonly", False),
                    settings.get("mask_character", "_"),
                    settings.get("margin", 20),
                    progress_callback=update_progress
                )
                print(f"[DEBUG] Generated {len(frames)} frames.")
                self.status_label.config(text=f"Generated {len(frames)} frames. Saving video...", fg="blue")
                # Create output folder in the program directory
                program_dir = os.path.dirname(os.path.abspath(__file__))
                output_folder = os.path.join(program_dir, 'xml-to-text-video-output')
                os.makedirs(output_folder, exist_ok=True)
                data_filename = os.path.splitext(os.path.basename(self.data_txt_path))[0]
                output_path = os.path.join(output_folder, f'{data_filename}_data.mp4')
                print(f"[DEBUG] Saving video to {output_path}...")
                self.save_video(frames, frame_times, output_path)
                print(f"[DEBUG] Video saved to {output_path}.")
                self.status_label.config(text=f"Video saved to {output_path}", fg="green")
                messagebox.showinfo("Done", f"Video saved to {output_path}")
                self.progress_data.stop()
                self.progress_data.pack_forget()
            except Exception as e:
                print(f"[DEBUG] Exception: {e}")
                self.status_label.config(text=f"Error: {e}", fg="red")
                messagebox.showerror("Error", str(e))
                self.progress_data.stop()
                self.progress_data.pack_forget()

        threading.Thread(target=do_generate, daemon=True).start()

    def generate_video_from_idfx(self):
        if not hasattr(self, 'idfx_path') or not self.idfx_path:
            messagebox.showerror("Error", "No .idfx file selected.")
            return
        self.status_label = getattr(self, 'status_label', None)
        if not self.status_label:
            self.status_label = tk.Label(self.tab3, text="Generating video, please wait...", fg="blue")
            self.status_label.pack(pady=5)
        else:
            self.status_label.config(text="Generating video, please wait...", fg="blue")
        self.root.update_idletasks()
        self.progress_idfx.pack(pady=5, fill="x", padx=10)
        self.progress_idfx.start()
        def do_generate():
            try:
                self.status_label.config(text="Parsing .idfx...", fg="blue")
                events = self.parse_idfx_events(self.idfx_path)
                self.status_label.config(text=f"Parsed {len(events)} events. Reconstructing text states...", fg="blue")
                settings = self.get_settings()
                text_states, frame_times = self.reconstruct_idfx_text_states(events, settings)
                if not text_states or not frame_times or len(text_states) != len(frame_times):
                    self.status_label.config(text="Error: No valid typing events found in file or data is malformed.", fg="red")
                    messagebox.showerror("Error", "No valid typing events found in file or data is malformed.")
                    self.progress_idfx.stop()
                    self.progress_idfx.pack_forget()
                    return
                font_family = settings["font_family"]
                font_size = settings["font_size"]
                bold = settings["bold"]
                def update_progress(current, total):
                    self.status_label.config(text=f"Generating frames: {current}/{total}", fg="blue")
                frames = self.generate_frames(
                    text_states, frame_times, font_family, font_size, bold,
                    settings.get("moving_window", False),
                    settings.get("window_size", 10),
                    settings.get("window_wordonly", False),
                    settings.get("mask_character", "_"),
                    settings.get("margin", 20),
                    progress_callback=update_progress
                )
                # Create output folder in the program directory
                program_dir = os.path.dirname(os.path.abspath(__file__))
                output_folder = os.path.join(program_dir, 'xml-to-text-video-output')
                os.makedirs(output_folder, exist_ok=True)
                idfx_filename = os.path.splitext(os.path.basename(self.idfx_path))[0]
                output_path = os.path.join(output_folder, f'{idfx_filename}_idfx.mp4')
                self.save_video(frames, frame_times, output_path)
                self.status_label.config(text=f"Video saved to {output_path}", fg="green")
                messagebox.showinfo("Done", f"Video saved to {output_path}")
                self.progress_idfx.stop()
                self.progress_idfx.pack_forget()
            except Exception as e:
                self.status_label.config(text=f"Error: {e}", fg="red")
                messagebox.showerror("Error", str(e))
                self.progress_idfx.stop()
                self.progress_idfx.pack_forget()
        threading.Thread(target=do_generate, daemon=True).start()

    def parse_xml_events(self, xml_path):
        tree = etree.parse(xml_path)
        root = tree.getroot()
        events = []
        for event in root.findall(".//event"):
            if event.findtext("type") == "keyboard":
                output = event.findtext("output")
                start_time = event.findtext("startTime")
                if output and start_time:
                    events.append({
                        'output': output,
                        'start_time': int(start_time)
                    })
        return events

    def reconstruct_text_states(self, events, settings):
        # If uniform typing mode is enabled, ignore events and use Word file
        if settings["uniform_typing"] and hasattr(self, 'word_path') and self.word_path:
            # Read text from Word file
            doc = Document(self.word_path)
            full_text = '\n'.join([p.text for p in doc.paragraphs])
            text_states = []
            frame_times = []
            chars_per_sec = settings["chars_per_sec"]
            interval = 1.0 / chars_per_sec if chars_per_sec > 0 else 0.1
            text = ""
            for c in full_text:
                text += c
                text_states.append(text)
                frame_times.append(interval)
            # Apply video speed multiplier
            speed_mult = settings["video_speed"]
            frame_times = [ft / speed_mult for ft in frame_times]
            return text_states, frame_times
        text = ""
        text_states = []
        frame_times = []
        last_time = 0
        for event in events:
            output = event['output']
            t = event['start_time'] / 1000.0  # ms to seconds
            if output == "SPACE":
                text += " "
            elif output == "BACK":
                text = text[:-1]
            elif output and len(output) == 1:
                text += output
            # Save state and time delta
            text_states.append(text)
            frame_times.append(max(t - last_time, 0.05))  # at least 0.05s per frame
            last_time = t
        # Adjust frame_times for word/space speed overrides
        word_speed = settings["word_speed"]
        space_duration = settings["space_duration"]
        for i, event in enumerate(events):
            output = event['output']
            if output == "SPACE":
                frame_times[i] = space_duration
            elif output and len(output) == 1:
                # Only set for the first char of a word (after a space or at start)
                if i == 0 or events[i-1]['output'] == "SPACE":
                    frame_times[i] = word_speed
        # Apply video speed multiplier
        speed_mult = settings["video_speed"]
        frame_times = [ft / speed_mult for ft in frame_times]
        return text_states, frame_times

    def parse_data_txt_events(self, data_txt_path):
        try:
            import ijson
        except ImportError:
            messagebox.showerror("Missing Dependency", "Please install the 'ijson' package to handle large data.txt files: pip install ijson")
            return []
        events = []
        time_accum = 0
        try:
            with open(data_txt_path, 'r') as f:
                print('DEBUG: Starting to parse data.txt with ijson')
                debug_count = 0
                found_any = False
                for entry in ijson.items(f, 'data.item'):
                    found_any = True
                    if debug_count < 5:
                        print('DEBUG ENTRY:', entry)
                        debug_count += 1
                    if not isinstance(entry, dict):
                        continue  # skip non-dict entries
                    key = entry.get('response_new_keyboard_response_1_1_4_1')
                    if key is None:
                        key = entry.get('response_new_keyboard_response_1_1_4')
                    t = entry.get('response_time_new_keyboard_response_1_1_4_1')
                    if t is None:
                        t = entry.get('response_time_new_keyboard_response_1_1_4')
                    if key is not None and t is not None:
                        time_accum += int(t)
                        events.append({'output': key, 'start_time': time_accum})
                if not found_any:
                    print('DEBUG: No items found in data.txt. Is it an empty file or not a top-level array?')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse data.txt: {e}")
            return []
        return events

    def parse_idfx_events(self, idfx_path):
        # Parse TypingDNA .idfx log structure into normalized events
        # Output format: {'output': one of 'space','enter','backspace' or single-character string, 'start_time': ms}
        events = []
        try:
            tree = etree.parse(idfx_path)
            root = tree.getroot()
            # Iterate keyboard events
            for event in root.findall(".//event[@type='keyboard']"):
                winlog = None
                for part in event.findall("part"):
                    if part.get("type") == "winlog":
                        winlog = part
                        break
                if winlog is None:
                    continue
                key = (winlog.findtext("key") or "").strip()
                val = winlog.findtext("value")
                start_time_txt = winlog.findtext("startTime")
                if start_time_txt is None:
                    continue
                try:
                    start_time = int(start_time_txt)
                except Exception:
                    continue
                # Normalize output
                output = None
                if key == "VK_SPACE":
                    output = "space"
                elif key == "VK_RETURN":
                    output = "enter"
                elif key in ("VK_BACK", "VK_BACKSPACE"):
                    output = "backspace"
                else:
                    # Use 'value' if present and printable single character
                    if val is not None and len(val) == 1:
                        output = val
                    else:
                        # Some logs may encode backspace as value "\u0008" (&#x8;)
                        if val is not None and (val == "\b" or val == "\u0008" or "#x8" in val):
                            output = "backspace"
                        else:
                            continue
                events.append({'output': output, 'start_time': start_time})
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse .idfx: {e}")
            return []
        return events

    def reconstruct_data_txt_text_states(self, events, settings):
        text = ""
        text_states = []
        frame_times = []
        last_time = 0
        valid_events = []
        for event in events:
            output = event['output']
            t = event['start_time'] / 1000.0  # ms to seconds
            if output == "space":
                text += " "
            elif output == "enter":
                text += "\n"
            elif output == "backspace":
                text = text[:-1]
            elif output and isinstance(output, str) and len(output) == 1:
                text += output
            else:
                continue  # skip events that don't add a char/space/enter/backspace
            text_states.append(text)
            frame_times.append(max(t - last_time, 0.05))
            last_time = t
            valid_events.append(event)
        # Adjust frame_times for word/space speed overrides
        word_speed = settings["word_speed"]
        space_duration = settings["space_duration"]
        for i, event in enumerate(valid_events):
            output = event['output']
            if output == "space":
                frame_times[i] = space_duration
            elif output and isinstance(output, str) and len(output) == 1:
                if i == 0 or valid_events[i-1]['output'] == "space":
                    frame_times[i] = word_speed
        speed_mult = settings["video_speed"]
        frame_times = [ft / speed_mult for ft in frame_times]
        return text_states, frame_times

    def reconstruct_idfx_text_states(self, events, settings):
        # Reuse the same logic as data.txt events (normalized outputs)
        return self.reconstruct_data_txt_text_states(events, settings)

    def _try_load_font_with_matplotlib(self, font_family, font_size, bold, font_manager):
        """Try to load font using matplotlib font manager"""
        if not font_manager:
            return None
        try:
            font_props = font_manager.FontProperties(family=font_family, weight='bold' if bold else 'normal')
            font_path = font_manager.findfont(font_props, fallback_to_default=False)
            if font_path and os.path.exists(font_path):
                from PIL import ImageFont
                return ImageFont.truetype(font_path, font_size)
        except Exception:
            pass
        return None

    def _try_load_system_fonts(self, font_family, font_size, bold):
        """Try to load common system fonts"""
        from PIL import ImageFont
        
        # Common font mappings
        font_mappings = {
            'Arial': ['arial', 'Arial', 'ArialMT'],
            'Times': ['times', 'Times', 'Times New Roman'],
            'Courier': ['courier', 'Courier', 'Courier New'],
            'Helvetica': ['helvetica', 'Helvetica'],
            'Verdana': ['verdana', 'Verdana'],
            'Georgia': ['georgia', 'Georgia'],
            'Comic Sans': ['comic', 'Comic Sans MS'],
        }
        
        # Try the exact font name first
        try:
            return ImageFont.truetype(font_family, font_size)
        except Exception:
            pass
        
        # Try mapped variations
        for base_name, variations in font_mappings.items():
            if font_family.lower() in [v.lower() for v in variations]:
                for variation in variations:
                    try:
                        return ImageFont.truetype(variation, font_size)
                    except Exception:
                        continue
        
        # Try system-specific paths
        if os.name == "nt":  # Windows
            font_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
            fallback = "arialbd.ttf" if bold else "arial.ttf"
            font_path = os.path.join(font_dir, fallback)
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except Exception:
                    pass
        elif os.name == "posix":  # macOS/Linux
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/TTF/arial.ttf"
            ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        return ImageFont.truetype(font_path, font_size)
                    except Exception:
                        continue
        
        return None

    def _try_load_pil_font(self, font_family, font_size, bold):
        """Try PIL's built-in font loading"""
        from PIL import ImageFont
        try:
            # Try common font names that PIL might recognize
            common_fonts = ['Arial', 'Helvetica', 'Times', 'Courier']
            for font_name in common_fonts:
                try:
                    return ImageFont.truetype(font_name, font_size)
                except Exception:
                    continue
        except Exception:
            pass
        return None

    def generate_frames(self, text_states, frame_times, font_family=None, font_size=None, bold=None, moving_window=False, window_size=10, window_wordonly=False, mask_character="_", margin=20, progress_callback=None):
        from PIL import ImageFont, Image, ImageDraw
        try:
            from matplotlib import font_manager
        except ImportError:
            font_manager = None
        
        # Use UI values as defaults if not provided
        if font_family is None:
            font_family = self.font_family_var.get()
        if font_size is None:
            font_size = self.font_size_var.get()
        if bold is None:
            bold = self.bold_var.get()
        if moving_window:
            window_size = self.window_size_var.get()
            window_wordonly = self.window_wordonly_var.get()
            mask_character = self.mask_character_var.get()
        if margin == 20:  # Only use UI margin if default was passed
            margin = self.margin_var.get()
        
        font = None
        font_loaded = True
        original_font_family = font_family
        
        # Try multiple font loading strategies
        font_strategies = [
            # Strategy 1: Try with matplotlib font manager
            lambda: self._try_load_font_with_matplotlib(font_family, font_size, bold, font_manager),
            # Strategy 2: Try common system fonts
            lambda: self._try_load_system_fonts(font_family, font_size, bold),
            # Strategy 3: Try PIL's built-in font loading
            lambda: self._try_load_pil_font(font_family, font_size, bold),
            # Strategy 4: Fallback to default
            lambda: ImageFont.load_default()
        ]
        
        for strategy in font_strategies:
            try:
                font = strategy()
                if font is not None:
                    break
            except Exception:
                continue
        
        # If we couldn't load the requested font, show a warning
        if font_loaded and font is not None:
            try:
                # Test if the font actually works
                test_img = Image.new("RGB", (10, 10))
                test_draw = ImageDraw.Draw(test_img)
                test_draw.text((0, 0), "Test", font=font)
            except Exception:
                font_loaded = False
        
        if not font_loaded:
            try:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Font Warning",
                    f"Could not load the selected font '{original_font_family}'. Using system default font instead."
                ))
            except Exception:
                pass
        width, height = 1280, 720
        frames = []
        blink_period = 1.0
        caret_width = 1
        caret_color = "black"
        last_text = None
        blink_time = 0.0
        for idx, text in enumerate(text_states):
            # Layout constants - use the margin parameter
            # Wrap text within the visible frame accounting for left+right margins
            lines = self.wrap_text(text, font, width - 2 * margin)
            if moving_window:
                # White background, show all text but mask characters outside window
                img = Image.new("RGB", (width, height), color="white")
                draw = ImageDraw.Draw(img)
                # Stable baseline line height for caret anchoring to avoid early-line jitter
                try:
                    ascent, descent = font.getmetrics()
                    base_line_h = ascent + descent
                except Exception:
                    base_bbox = draw.textbbox((0, 0), "Ag", font=font)
                    base_line_h = (base_bbox[3] - base_bbox[1]) if base_bbox else font_size
                
                # Get the final text to show full text from the beginning
                final_text = text_states[-1] if text_states else ""
                final_lines = self.wrap_text(final_text, font, width - 2 * margin)
                
                # Calculate window boundaries centered on the caret position
                # Double the UI window size for the actual moving window
                actual_window_size = window_size * 2
                caret_pos = len(text)
                half_window = actual_window_size // 2
                
                # Always try to show exactly actual_window_size characters
                if len(final_text) <= actual_window_size:
                    # Text is shorter than window - show all text
                    window_start = 0
                    window_end = len(final_text)
                elif caret_pos <= half_window:
                    # Near the beginning - show first actual_window_size characters
                    window_start = 0
                    window_end = actual_window_size
                elif caret_pos >= len(final_text) - half_window:
                    # Near the end - show last actual_window_size characters
                    window_start = len(final_text) - actual_window_size
                    window_end = len(final_text)
                else:
                    # In the middle - center the window around caret
                    window_start = caret_pos - half_window
                    window_end = window_start + actual_window_size
                
                # Draw the complete final text with hiding characters
                y = margin
                char_idx = 0
                last_line_y = y
                caret_x = margin
                caret_y = margin
                
                # Draw ALL final lines with proper spacing
                for i, line in enumerate(final_lines):
                    x = margin
                    for c in line:
                        # Calculate the actual character index in the final text
                        actual_char_idx = char_idx
                        
                        # Determine if this character should be visible based on window position
                        should_show = window_start <= actual_char_idx < window_end
                        
                        if should_show:
                            # Show the actual character (only if it's been typed)
                            if actual_char_idx < len(text):
                                draw.text((x, y), c, font=font, fill="black")
                                # Use natural character spacing for readable text
                                char_width = draw.textbbox((x, y), c, font=font)[2] - draw.textbbox((x, y), c, font=font)[0]
                            else:
                                # Show mask character for untyped text
                                draw.text((x, y), mask_character, font=font, fill="black")
                                # Use mask character width for consistent spacing
                                char_width = draw.textbbox((x, y), mask_character, font=font)[2] - draw.textbbox((x, y), mask_character, font=font)[0]
                        else:
                            # Show the mask character (respecting line breaks)
                            if c == '\n':
                                # Keep newlines as newlines but mask the character
                                draw.text((x, y), '\n', font=font, fill="black")
                                char_width = 0  # Newlines don't advance x position
                            else:
                                # Replace with mask character
                                draw.text((x, y), mask_character, font=font, fill="black")
                                # Use mask character width for even spacing
                                char_width = draw.textbbox((x, y), mask_character, font=font)[2] - draw.textbbox((x, y), mask_character, font=font)[0]
                        
                        x += char_width
                        char_idx += 1
                        
                        # Update caret position as we go (accounting for actual character widths)
                        if actual_char_idx == len(text) - 1:  # Last character
                            caret_x = x
                            caret_y = y
                    
                    # Track the last line for caret positioning
                    if i == len(final_lines) - 1:
                        last_line_y = y
                    
                    # Advance by exactly one baseline height (no extra spacing)
                    y += base_line_h
                
                # Caret position is already calculated in the drawing loop above
                caret_h = max(1, int(round(font_size * 0.9)))
            else:
                # White background, draw all wrapped text in black
                img = Image.new("RGB", (width, height), color="white")
                draw = ImageDraw.Draw(img)
                # Stable baseline line height for caret anchoring to avoid early-line jitter
                try:
                    ascent, descent = font.getmetrics()
                    base_line_h = ascent + descent
                except Exception:
                    base_bbox = draw.textbbox((0, 0), "Ag", font=font)
                    base_line_h = (base_bbox[3] - base_bbox[1]) if base_bbox else font_size
                caret_h = max(1, int(round(font_size * 0.9)))
                
                # Calculate how many lines can fit in the visible area
                available_height = height - 2 * margin
                max_visible_lines = max(1, available_height // base_line_h)
                
                # Auto-scroll: if we have more lines than can fit, start from a later line
                start_line_idx = 0
                if len(lines) > max_visible_lines:
                    # Start from the line that puts the last line at the bottom
                    start_line_idx = max(0, len(lines) - max_visible_lines)
                
                # Draw only the visible lines
                y = margin
                last_line_y = y
                visible_lines = lines[start_line_idx:start_line_idx + max_visible_lines]
                
                for i, line in enumerate(visible_lines):
                    actual_line_idx = start_line_idx + i
                    draw.text((margin, y), line, font=font, fill="black")
                    bbox = draw.textbbox((margin, y), line, font=font)
                    line_height = bbox[3] - bbox[1]
                    if actual_line_idx == len(lines) - 1:
                        last_line_y = y
                        # Use baseline height to determine line bottom consistently
                        last_line_height = base_line_h
                    # Advance by exactly one baseline height (no extra spacing)
                    y += base_line_h
                
                # Place caret at the end of the last line
                if lines:
                    last_line = lines[-1]
                    safe_last_line = last_line.split('\n')[-1]
                    caret_x = margin + draw.textlength(safe_last_line, font=font)
                    # Shorter fixed caret height (0.9x font size); bottom anchored to baseline
                    caret_h = max(1, int(round(font_size * 0.9)))
                    caret_y = last_line_y + base_line_h - caret_h - 2
                else:
                    caret_h = max(1, int(round(font_size * 0.9)))
                    caret_x, caret_y = margin, margin + base_line_h - caret_h - 2
            # Blinking caret logic with reset on new character
            if last_text is None or text != last_text:
                blink_time = 0.0
                caret_visible = True
            else:
                caret_visible = ((blink_time % blink_period) < (blink_period / 2))
            if caret_visible:
                draw.rectangle(
                    [caret_x, caret_y, caret_x + caret_width, caret_y + caret_h],
                    fill=caret_color
                )
            frames.append(img)
            last_text = text
            if idx < len(frame_times):
                blink_time += frame_times[idx]
            if progress_callback and idx % 100 == 0:
                progress_callback(idx, len(text_states))
        return frames

    def wrap_text(self, text, font, max_width):
        # Handle both explicit newlines and word wrapping
        dummy_img = Image.new("RGB", (10, 10))
        draw = ImageDraw.Draw(dummy_img)
        
        # First split by explicit newlines
        paragraphs = text.split('\n')
        lines = []
        
        for paragraph in paragraphs:
            if not paragraph:  # Empty paragraph from consecutive newlines
                lines.append('')
                continue
                
            # Word wrap within each paragraph
            words = paragraph.split(' ')
            line = ''
            for word in words:
                test_line = line + (' ' if line else '') + word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_width:
                    line = test_line
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
        
        return lines

    def save_video(self, frames, frame_times, output_path):
        # Convert PIL images to numpy arrays
        import numpy as np
        frame_arrays = [np.array(f) for f in frames]
        # Use frame_times as durations
        durations = frame_times
        # MoviePy expects fps, so we use variable durations by repeating frames
        # We'll use a workaround: create a list of (frame, duration) pairs
        clips = []
        for arr, dur in zip(frame_arrays, durations):
            clips.append((arr, dur))
        # Flatten to frames at 20 fps
        fps = 20
        video_frames = []
        for arr, dur in clips:
            count = max(1, int(round(dur * fps)))
            video_frames.extend([arr] * count)
        clip = ImageSequenceClip(video_frames, fps=fps)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        clip.write_videofile(output_path, codec='libx264', audio=False)

    def preview_video(self):
        # Generate and preview the video in a separate thread to avoid blocking the GUI
        def do_preview():
            try:
                events = self.parse_xml_events(self.xml_path)
                text_states, frame_times = self.reconstruct_text_states(events, self.get_settings())
                font_family = self.font_family_var.get()
                font_size = self.font_size_var.get()
                bold = self.bold_var.get()
                frames = self.generate_frames(
                    text_states, frame_times, font_family, font_size, bold,
                    self.moving_window_var.get(),
                    self.window_size_var.get(),
                    self.window_wordonly_var.get(),
                    self.mask_character_var.get(),
                    self.margin_var.get()
                )
                # Save to a temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmpfile:
                    temp_path = tmpfile.name
                self.save_video(frames, frame_times, temp_path)
                # Play the video using the default system player
                if os.name == 'nt':
                    os.startfile(temp_path)
                else:
                    import subprocess
                    subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', temp_path])
            except Exception as e:
                messagebox.showerror("Preview Error", str(e))
        threading.Thread(target=do_preview, daemon=True).start()

    def get_settings(self):
        return {
            "font_family": self.font_family_var.get(),
            "font_size": self.font_size_var.get(),
            "bold": self.bold_var.get(),
            "margin": self.margin_var.get(),
            "uniform_typing": self.uniform_typing_var.get(),
            "chars_per_sec": self.chars_per_sec_var.get(),
            "video_speed": self.video_speed_var.get(),
            "word_speed": self.word_speed_var.get(),
            "space_duration": self.space_duration_var.get(),
            "save_video": self.save_video_var.get(),
            "moving_window": self.moving_window_var.get(),
            "window_size": self.window_size_var.get(),
            "window_wordonly": self.window_wordonly_var.get(),
            "mask_character": self.mask_character_var.get()
        }

    def set_settings(self, settings):
        self.font_family_var.set(settings.get("font_family", "Arial"))
        self.font_size_var.set(settings.get("font_size", 30))
        self.bold_var.set(settings.get("bold", True))
        self.margin_var.set(settings.get("margin", 20))
        self.uniform_typing_var.set(settings.get("uniform_typing", False))
        self.chars_per_sec_var.set(settings.get("chars_per_sec", 10.0))
        self.video_speed_var.set(settings.get("video_speed", 1.0))
        self.word_speed_var.set(settings.get("word_speed", 0.15))
        self.space_duration_var.set(settings.get("space_duration", 0.25))
        self.save_video_var.set(settings.get("save_video", True))
        self.moving_window_var.set(settings.get("moving_window", False))
        self.window_size_var.set(settings.get("window_size", 10))
        self.window_wordonly_var.set(settings.get("window_wordonly", False))
        self.mask_character_var.set(settings.get("mask_character", "_"))
        self.update_window_controls()

    def save_settings(self):
        settings = self.get_settings()
        try:
            # Save settings in the program directory
            program_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(program_dir, 'xml-to-text-settings.json')
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Settings Saved", f"Settings saved to {settings_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def load_settings(self):
        try:
            # Load settings from program directory
            program_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(program_dir, 'xml-to-text-settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                self.set_settings(settings)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")

    def update_window_controls(self):
        if self.moving_window_var.get():
            self.window_size_entry.config(state="normal")
            self.window_wordonly_check.config(state="normal")
            self.mask_character_entry.config(state="normal")
        else:
            self.window_size_entry.config(state="disabled")
            self.window_wordonly_check.config(state="disabled")
            self.mask_character_entry.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLToVideoApp(root)
    root.mainloop() 