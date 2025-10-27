#!/usr/bin/env python3
"""
Cross-Platform Cursor Mover for Windows and Linux
Uses tkinter for a simple GUI interface
"""

import tkinter as tk
from tkinter import messagebox
import pyautogui
import random
import threading
import time
import sys

pyautogui.FAILSAFE = False


class CursorMoverGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cursor Mover")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"400x300+{x}+{y}")
        
        # State variables
        self.running = False
        self.interval = 11
        self.thread = None
        
        # Get screen size
        try:
            self.screen_width, self.screen_height = pyautogui.size()
        except Exception:
            self.screen_width, self.screen_height = (1920, 1080)
        
        self.create_ui()
        
    def create_ui(self):
        # Title
        title = tk.Label(
            self.root,
            text="Cursor Mover",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=20)
        
        # Status frame
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: 🔴 Inactive",
            font=("Arial", 14),
            fg="red"
        )
        self.status_label.pack()
        
        # Interval frame
        interval_frame = tk.Frame(self.root)
        interval_frame.pack(pady=10)
        
        tk.Label(
            interval_frame,
            text="Interval (seconds):",
            font=("Arial", 10)
        ).pack()
        
        self.interval_var = tk.StringVar(value=str(self.interval))
        interval_entry = tk.Entry(
            interval_frame,
            textvariable=self.interval_var,
            width=10,
            font=("Arial", 12),
            justify="center"
        )
        interval_entry.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.action_button = tk.Button(
            button_frame,
            text="Start Movement",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.toggle_movement,
            relief="flat",
            borderwidth=0,
            activebackground="#45a049"
        )
        self.action_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Quit",
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.quit_app,
            relief="flat",
            borderwidth=0,
            activebackground="#da190b"
        ).pack(side=tk.LEFT, padx=5)
        
        # Info
        info_label = tk.Label(
            self.root,
            text=f"Screen: {self.screen_width} × {self.screen_height}",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(side=tk.BOTTOM, pady=10)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
    
    def toggle_movement(self):
        if not self.running:
            self.start_movement()
        else:
            self.stop_movement()
    
    def start_movement(self):
        try:
            interval = int(self.interval_var.get())
            if interval < 10:
                messagebox.showerror("Error", "Interval must be at least 10 seconds")
                return
            self.interval = interval
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return
        
        # Check permissions
        try:
            _ = pyautogui.position()
        except Exception:
            messagebox.showinfo(
                "Permission Required",
                "Please grant Accessibility/Input permission in System Settings"
            )
            return
        
        self.running = True
        self.status_label.config(text="Status: 🟢 Active", fg="green")
        self.action_button.config(text="Stop Movement", bg="#f44336", activebackground="#da190b")
        self.root.title("Cursor Mover - Running")
        
        # Start thread
        self.thread = threading.Thread(target=self.move_cursor_loop, daemon=True)
        self.thread.start()
        
        messagebox.showinfo("Started", f"Cursor will move every {self.interval} seconds")
    
    def stop_movement(self):
        self.running = False
        self.status_label.config(text="Status: 🔴 Inactive", fg="red")
        self.action_button.config(text="Start Movement", bg="#4CAF50", activebackground="#45a049")
        self.root.title("Cursor Mover")
        
        messagebox.showinfo("Stopped", "Cursor movement has been stopped")
    
    def move_cursor_loop(self):
        while self.running:
            x = random.randint(0, self.screen_width - 1)
            y = random.randint(0, self.screen_height - 1)
            
            try:
                pyautogui.moveTo(x, y, duration=0.25)
            except Exception as e:
                print(f"Error moving cursor: {e}")
                self.running = False
                self.root.after(0, self.stop_movement)
                return
            
            # Wait for interval
            for _ in range(self.interval * 2):
                if not self.running:
                    return
                time.sleep(0.5)
    
    def quit_app(self):
        if self.running:
            self.stop_movement()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CursorMoverGUI()
    app.run()

