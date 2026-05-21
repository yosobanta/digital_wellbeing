import tkinter as tk
from tkinter import ttk
from database import get_daily_usage
from datetime import date
import os
import psutil
import subprocess

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import STOP_FLAG_PATH

def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "< 1m"

def is_tracker_running():
    for p in psutil.process_iter(['name']):
        try:
            if 'digital_wellbeing.exe' in p.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def start_tracker(status_label, start_btn, stop_btn):
    exe_path = os.path.join(os.path.dirname(__file__), "dist", "digital_wellbeing", "digital_wellbeing.exe")
    if not os.path.exists(exe_path):
        status_label.config(text="Status: EXE Not Found!", fg="#dc2626")
        return
        
    try:
        # Launch detached process without console window
        CREATE_NO_WINDOW = 0x08000000
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen([exe_path], creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS)
        
        status_label.config(text="Status: Starting...", fg="#d97706")
        start_btn.config(state=tk.DISABLED)
        
        # Wait a bit and update status
        status_label.after(2000, lambda: check_tracker_status(status_label, start_btn, stop_btn))
    except Exception as e:
        status_label.config(text="Status: Error Starting", fg="#dc2626")
        print(f"Error starting tracker: {e}")

def stop_tracker(status_label, start_btn, stop_btn):
    # Create the flag file
    with open(STOP_FLAG_PATH, 'w') as f:
        f.write("stop")
    
    status_label.config(text="Status: Stopping...", fg="#d97706")
    stop_btn.config(state=tk.DISABLED)
    
    # Wait a bit and update status
    status_label.after(2000, lambda: check_tracker_status(status_label, start_btn, stop_btn))

def check_tracker_status(status_label, start_btn, stop_btn):
    if is_tracker_running():
        status_label.config(text="Status: Running", fg="#059669")
        stop_btn.config(state=tk.NORMAL)
        start_btn.config(state=tk.DISABLED)
    else:
        status_label.config(text="Status: Stopped", fg="#dc2626")
        stop_btn.config(state=tk.DISABLED)
        start_btn.config(state=tk.NORMAL)

def load_data(tree, fig, canvas, total_label):
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
        
    usage_data = get_daily_usage()
    
    fig.clear()
    
    if not usage_data:
        tree.insert("", "end", values=("No usage data yet for today.", ""))
        total_label.config(text="Total Usage: 0m")
        # Draw empty chart
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No data available", horizontalalignment='center', verticalalignment='center')
        ax.axis('off')
        canvas.draw()
        return

    labels = []
    sizes = []
    total_all_seconds = 0
    
    for app_name, total_seconds in usage_data:
        duration_str = format_duration(total_seconds)
        tree.insert("", "end", values=(app_name, duration_str))
        labels.append(app_name)
        sizes.append(total_seconds)
        total_all_seconds += total_seconds
        
    total_label.config(text=f"Total Usage: {format_duration(total_all_seconds)}")
        
    # Draw Pie Chart
    # Limit to top 5 for cleaner pie chart, group rest as "Other"
    if len(sizes) > 6:
        top_sizes = sizes[:5]
        top_labels = labels[:5]
        other_size = sum(sizes[5:])
        top_sizes.append(other_size)
        top_labels.append("Other")
    else:
        top_sizes = sizes
        top_labels = labels

    ax = fig.add_subplot(111)
    ax.pie(top_sizes, labels=top_labels, autopct='%1.1f%%', startangle=140, 
           textprops={'fontsize': 9}, colors=matplotlib.cm.Set3.colors)
    ax.axis('equal')
    fig.tight_layout()
    canvas.draw()

def create_gui():
    root = tk.Tk()
    root.title("Digital Wellbeing Dashboard")
    root.geometry("800x600")
    
    root.configure(bg="#ffffff")
    
    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("Treeview", background="#ffffff", foreground="#333333", rowheight=30, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f8f9fa", foreground="#111827", relief="flat")
    
    # Main Paned Window
    main_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Header Frame
    header_frame = tk.Frame(main_frame, bg="#ffffff")
    header_frame.pack(fill=tk.X, pady=(0, 20))
    
    today_str = date.today().strftime("%A, %B %d, %Y")
    
    title_frame = tk.Frame(header_frame, bg="#ffffff")
    title_frame.pack(side=tk.LEFT)
    
    tk.Label(title_frame, text="Daily Dashboard", font=("Segoe UI", 20, "bold"), bg="#ffffff", fg="#111827").pack(anchor="w")
    
    subtitle_frame = tk.Frame(title_frame, bg="#ffffff")
    subtitle_frame.pack(anchor="w")
    
    tk.Label(subtitle_frame, text=today_str, font=("Segoe UI", 11), bg="#ffffff", fg="#6b7280").pack(side=tk.LEFT, padx=(0, 15))
    
    total_label = tk.Label(subtitle_frame, text="Total Usage: Calculating...", font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#4f46e5")
    total_label.pack(side=tk.LEFT)
    
    # Controls Frame (Tracker Status)
    controls_frame = tk.Frame(header_frame, bg="#f3f4f6", padx=10, pady=10, relief=tk.FLAT)
    controls_frame.pack(side=tk.RIGHT)
    
    status_label = tk.Label(controls_frame, text="Status: Checking...", font=("Segoe UI", 10, "bold"), bg="#f3f4f6")
    status_label.pack(side=tk.LEFT, padx=(0, 15))
    
    start_btn = tk.Button(controls_frame, text="Start Tracker", font=("Segoe UI", 9, "bold"), 
                         bg="#d1fae5", fg="#065f46", relief=tk.FLAT, cursor="hand2", padx=10, pady=3,
                         command=lambda: start_tracker(status_label, start_btn, stop_btn))
    start_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    stop_btn = tk.Button(controls_frame, text="Stop Tracker", font=("Segoe UI", 9, "bold"), 
                         bg="#fee2e2", fg="#991b1b", relief=tk.FLAT, cursor="hand2", padx=10, pady=3,
                         command=lambda: stop_tracker(status_label, start_btn, stop_btn))
    stop_btn.pack(side=tk.LEFT)
    
    # Content Frame
    content_frame = tk.Frame(main_frame, bg="#ffffff")
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Left side: Treeview
    left_frame = tk.Frame(content_frame, bg="#ffffff")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    columns = ("App", "Duration")
    tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="none")
    tree.heading("App", text="Application", anchor="w")
    tree.heading("Duration", text="Usage Time", anchor="e")
    tree.column("App", width=200, anchor="w")
    tree.column("Duration", width=100, anchor="e")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    
    # Right side: Graph
    right_frame = tk.Frame(content_frame, bg="#ffffff")
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    fig = Figure(figsize=(4, 4), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Bottom actions
    bottom_frame = tk.Frame(main_frame, bg="#ffffff")
    bottom_frame.pack(fill=tk.X, pady=(15, 0))
    
    tk.Button(bottom_frame, text="Refresh Data", font=("Segoe UI", 10), bg="#f3f4f6", fg="#374151", 
              relief=tk.FLAT, cursor="hand2", padx=15, pady=5,
              command=lambda: load_data(tree, fig, canvas, total_label)).pack(side=tk.RIGHT)
    
    # Initial load
    check_tracker_status(status_label, start_btn, stop_btn)
    load_data(tree, fig, canvas, total_label)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
