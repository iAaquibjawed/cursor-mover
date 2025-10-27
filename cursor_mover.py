#!/usr/bin/env python3
"""
Modern Random Cursor Mover - CustomTkinter Version
Beautiful macOS-style UI
"""

import customtkinter as ctk
import pyautogui
import random
import time
import threading
import sys
import subprocess
from tkinter import messagebox

pyautogui.FAILSAFE = False


class CursorMoverApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App window settings
        self.title("Random Cursor Mover")
        self.geometry("420x480")
        self.resizable(False, False)

        # CustomTkinter global appearance
        ctk.set_appearance_mode("light")  # "light" or "dark"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

        # App state
        self.running = False
        self.interval = 120
        self.thread = None

        # Get screen size
        try:
            self.screen_width, self.screen_height = pyautogui.size()
        except Exception:
            self.screen_width, self.screen_height = (1920, 1080)

        # Build UI
        self.create_ui()

    def create_ui(self):
        # Header
        self.icon_label = ctk.CTkLabel(self, text="🖱️", font=("SF Pro Display", 40))
        self.icon_label.pack(pady=(25, 10))

        self.title_label = ctk.CTkLabel(self, text="Cursor Mover",
                                        font=("SF Pro Display", 26, "bold"))
        self.title_label.pack(pady=(0, 4))

        self.subtitle_label = ctk.CTkLabel(self, text="Automatically move your cursor at intervals",
                                           font=("SF Pro Text", 12), text_color="#666")
        self.subtitle_label.pack(pady=(0, 25))

        # Status Card
        self.status_frame = ctk.CTkFrame(self, corner_radius=12)
        self.status_frame.pack(padx=40, pady=(0, 15), fill="x")

        ctk.CTkLabel(self.status_frame, text="Status",
                     font=("SF Pro Text", 12), text_color="#999").pack(pady=(10, 0))

        self.status_dot = ctk.CTkLabel(self.status_frame, text="●",
                                       font=("SF Pro Text", 22), text_color="#AAA")
        self.status_dot.pack(pady=(4, 0))

        self.status_label = ctk.CTkLabel(self.status_frame, text="Inactive",
                                         font=("SF Pro Display", 15, "bold"),
                                         text_color="#AAA")
        self.status_label.pack(pady=(0, 10))

        # Interval Card
        self.interval_frame = ctk.CTkFrame(self, corner_radius=12)
        self.interval_frame.pack(padx=40, pady=10, fill="x")

        ctk.CTkLabel(self.interval_frame, text="Interval (seconds)",
                     font=("SF Pro Text", 12), text_color="#999").pack(pady=(10, 5))

        self.interval_var = ctk.StringVar(value="120")
        self.interval_entry = ctk.CTkEntry(self.interval_frame, textvariable=self.interval_var,
                                           justify="center", font=("SF Pro Text", 16))
        self.interval_entry.pack(padx=40, pady=(5, 15))

        # Start/Stop Button
        self.action_button = ctk.CTkButton(self,
                                           text="Start Movement",
                                           font=("SF Pro Display", 18, "bold"),
                                           corner_radius=10,
                                           height=50,
                                           fg_color="#007AFF",
                                           hover_color="#005FCC",
                                           command=self.toggle_movement)
        self.action_button.pack(pady=(25, 10), padx=60, fill="x")

        # Footer
        ctk.CTkLabel(self, text=f"Screen: {self.screen_width} × {self.screen_height}",
                     font=("SF Pro Text", 11),
                     text_color="#888").pack(side="bottom", pady=15)

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

        try:
            _ = pyautogui.position()
        except Exception:
            self.show_permission_instructions()
            return

        self.running = True
        self.update_ui_state(active=True)
        self.thread = threading.Thread(target=self.move_cursor_loop, daemon=True)
        self.thread.start()

    def stop_movement(self):
        self.running = False
        self.update_ui_state(active=False)

    def update_ui_state(self, active: bool):
        if active:
            self.status_label.configure(text="Active", text_color="#4CAF50")
            self.status_dot.configure(text_color="#4CAF50")
            self.action_button.configure(text="Stop Movement",
                                         fg_color="#FF3B30",
                                         hover_color="#E62E2E")
        else:
            self.status_label.configure(text="Inactive", text_color="#AAA")
            self.status_dot.configure(text_color="#AAA")
            self.action_button.configure(text="Start Movement",
                                         fg_color="#007AFF",
                                         hover_color="#005FCC")

    def move_cursor_loop(self):
        while self.running:
            time.sleep(self.interval)
            if not self.running:
                break
            x = random.randint(0, self.screen_width - 1)
            y = random.randint(0, self.screen_height - 1)
            pyautogui.moveTo(x, y, duration=0.2)

    def show_permission_instructions(self):
        messagebox.showinfo(
            "Permission Required",
            "CursorMover needs Accessibility permission:\n\n"
            "1. System Settings will open\n"
            "2. Enable 'Terminal' or 'CursorMover'\n"
            "3. Retry after enabling access."
        )
        try:
            subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
        except Exception:
            pass


if __name__ == "__main__":
    app = CursorMoverApp()
    app.mainloop()




#!/usr/bin/env python3
# """
# Random Cursor Mover - macOS Menu Bar App + Modern GUI Panel
# """

# import rumps
# import pyautogui
# import random
# import threading
# import time
# import customtkinter as ctk
# from tkinter import messagebox

# pyautogui.FAILSAFE = False


# # -----------------------------
# # Modern GUI Window (CustomTkinter)
# # -----------------------------
# class CursorMoverGUI(ctk.CTk):
#     def __init__(self, controller):
#         super().__init__()
#         self.controller = controller
#         self.title("Cursor Mover Control Panel")
#         self.geometry("400x420")
#         self.resizable(False, False)

#         ctk.set_appearance_mode("light")
#         ctk.set_default_color_theme("blue")

#         self.interval = ctk.StringVar(value="120")

#         # Header
#         ctk.CTkLabel(self, text="🖱️", font=("SF Pro Display", 42)).pack(pady=(20, 10))
#         ctk.CTkLabel(self, text="Cursor Mover", font=("SF Pro Display", 24, "bold")).pack()
#         ctk.CTkLabel(self, text="Automatically move your cursor at intervals",
#                      font=("SF Pro Text", 12), text_color="#666").pack(pady=(0, 20))

#         # Status card
#         self.status_label = ctk.CTkLabel(self, text="Status: Inactive",
#                                          font=("SF Pro Display", 14, "bold"), text_color="#999")
#         self.status_label.pack(pady=(0, 15))

#         # Interval input
#         ctk.CTkLabel(self, text="Interval (seconds)", font=("SF Pro Text", 12),
#                      text_color="#888").pack()
#         self.interval_entry = ctk.CTkEntry(self, textvariable=self.interval,
#                                            justify="center", font=("SF Pro Text", 16))
#         self.interval_entry.pack(padx=80, pady=(5, 20))

#         # Start/Stop Button
#         self.start_button = ctk.CTkButton(self, text="Start Movement",
#                                           font=("SF Pro Display", 18, "bold"),
#                                           corner_radius=10, height=45,
#                                           fg_color="#007AFF", hover_color="#005FCC",
#                                           command=self.toggle_movement)
#         self.start_button.pack(pady=(10, 15), padx=80, fill="x")

#         # Close button
#         ctk.CTkButton(self, text="Close Window", font=("SF Pro Text", 13),
#                       fg_color="#E0E0E0", text_color="#333",
#                       hover_color="#CCCCCC", command=self.withdraw).pack(pady=(5, 15))

#     def toggle_movement(self):
#         if self.controller.running:
#             self.controller.stop_movement()
#             self.update_ui(active=False)
#         else:
#             try:
#                 interval = int(self.interval.get())
#                 if interval < 10:
#                     messagebox.showerror("Error", "Interval must be at least 10 seconds")
#                     return
#                 self.controller.interval = interval
#                 self.controller.start_movement()
#                 self.update_ui(active=True)
#             except ValueError:
#                 messagebox.showerror("Error", "Please enter a valid number")

#     def update_ui(self, active):
#         if active:
#             self.status_label.configure(text="Status: Active", text_color="#4CAF50")
#             self.start_button.configure(text="Stop Movement",
#                                         fg_color="#FF3B30", hover_color="#E62E2E")
#         else:
#             self.status_label.configure(text="Status: Inactive", text_color="#999")
#             self.start_button.configure(text="Start Movement",
#                                         fg_color="#007AFF", hover_color="#005FCC")


# # -----------------------------
# # Menu Bar App Controller (rumps)
# # -----------------------------
# class CursorMoverController(rumps.App):
#     def __init__(self):
#         super(CursorMoverController, self).__init__("🖱️", title="Cursor Mover")
#         self.interval = 120
#         self.running = False
#         self.thread = None
#         self.gui = None

#         self.menu = [
#             rumps.MenuItem("Open Control Panel", callback=self.open_gui),
#             None,
#             rumps.MenuItem("Quit", callback=rumps.quit_application)
#         ]

#     def open_gui(self, sender=None):
#         if not self.gui:
#             self.gui = CursorMoverGUI(self)
#         self.gui.deiconify()
#         self.gui.lift()

#     def start_movement(self):
#         if not self.running:
#             self.running = True
#             self.thread = threading.Thread(target=self.move_cursor_loop, daemon=True)
#             self.thread.start()
#             rumps.notification("Cursor Mover", "Started",
#                                f"Moving every {self.interval} seconds")

#     def stop_movement(self):
#         self.running = False
#         rumps.notification("Cursor Mover", "Stopped", "Cursor movement disabled")

#     def move_cursor_loop(self):
#         while self.running:
#             time.sleep(self.interval)
#             if not self.running:
#                 break
#             x = random.randint(0, pyautogui.size().width - 1)
#             y = random.randint(0, pyautogui.size().height - 1)
#             pyautogui.moveTo(x, y, duration=0.2)


# if __name__ == "__main__":
#     app = CursorMoverController()
#     app.run()
