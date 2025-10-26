#!/usr/bin/env python3
"""
Random Cursor Mover - Desktop Application
A cross-platform desktop app that moves your cursor to random positions.
"""

import pyautogui
import random
import time
import sys
import threading
import traceback
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# Disable PyAutoGUI failsafe (optional)
pyautogui.FAILSAFE = False


class CursorMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Cursor Mover")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        # State variables
        self.running = False
        self.thread = None
        self.interval = 120  # Default: 2 minutes

        # Get screen size (try to get it, use fallback if fails)
        try:
            self.screen_width, self.screen_height = pyautogui.size()
        except Exception as e:
            print(f"Could not get screen size: {e}")
            self.screen_width = 1920
            self.screen_height = 1080

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = Label(self.root, text="Random Cursor Mover",
                           font=("Arial", 18, "bold"))
        title_label.pack(pady=15)

        # Description
        desc_label = Label(self.root,
                          text="Moves cursor to random positions",
                          font=("Arial", 10))
        desc_label.pack(pady=5)

        # Status frame
        status_frame = Frame(self.root)
        status_frame.pack(pady=15)

        status_label = Label(status_frame, text="Status:", font=("Arial", 11))
        status_label.pack(side=LEFT, padx=5)

        self.status_label = Label(status_frame, text="Inactive",
                                 font=("Arial", 11), fg="gray")
        self.status_label.pack(side=LEFT, padx=5)

        # Interval frame
        interval_frame = Frame(self.root)
        interval_frame.pack(pady=10)

        interval_label = Label(interval_frame, text="Interval (seconds):",
                              font=("Arial", 11))
        interval_label.pack(side=LEFT, padx=5)

        self.interval_var = StringVar(value="120")
        interval_entry = Entry(interval_frame, textvariable=self.interval_var,
                              width=10)
        interval_entry.pack(side=LEFT, padx=5)

        # Buttons frame
        buttons_frame = Frame(self.root)
        buttons_frame.pack(pady=25)

        self.start_button = Button(buttons_frame, text="Start",
                                  command=self.start_movement,
                                  bg="#4CAF50", fg="white",
                                  font=("Arial", 12, "bold"),
                                  width=12, height=2,
                                  activebackground="#45a049")
        self.start_button.pack(side=LEFT, padx=10)

        self.stop_button = Button(buttons_frame, text="Stop",
                                 command=self.stop_movement,
                                 bg="#f44336", fg="white",
                                 font=("Arial", 12, "bold"),
                                 width=12, height=2,
                                 state=DISABLED,
                                 activebackground="#da190b")
        self.stop_button.pack(side=LEFT, padx=10)

        # Info frame
        info_frame = Frame(self.root)
        info_frame.pack(pady=10)

        screen_info = Label(info_frame,
                           text=f"Screen: {self.screen_width}x{self.screen_height}",
                           font=("Arial", 9), fg="gray")
        screen_info.pack()

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def start_movement(self):
        # Get interval from entry
        try:
            self.interval = int(self.interval_var.get())
            if self.interval < 10:
                messagebox.showerror("Error", "Interval must be at least 10 seconds")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return

        if self.running:
            return

        # CRITICAL: Test if we have accessibility permission
        # This triggers the permission dialog if not granted
        try:
            test_pos = pyautogui.position()
            print(f"Permission OK - Current position: {test_pos}")
        except Exception as e:
            print(f"Permission check failed: {e}")
            # Show instructions and open System Settings
            self.show_permission_instructions()
            return

        self.running = True
        self.status_label.config(text="Active", fg="green")
        self.start_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)

        # Start cursor movement in separate thread
        self.thread = threading.Thread(target=self.move_cursor_loop, daemon=True)
        self.thread.start()

        # Show starting notification
        self.show_notification("Cursor movement started",
                              f"Moving every {self.interval} seconds")

    def show_permission_instructions(self):
        """Show instructions for granting accessibility permission"""
        instructions = (
            "Accessibility Permission Required\n\n"
            "CursorMover needs permission to move your cursor.\n\n"
            "1. A System Settings window will open\n"
            "2. In the list, find 'CursorMover' or 'Terminal'\n"
            "3. Enable the toggle next to it\n"
            "4. Return here and click 'Start' again\n\n"
            "Note: The app must appear in the list after you click 'Start'."
        )

        # Show the instruction dialog
        result = messagebox.showinfo("Permission Required", instructions)

        # Open System Settings to Accessibility
        try:
            import subprocess
            subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
            print("Opening System Settings to Accessibility...")
        except Exception as e:
            print(f"Could not open System Settings: {e}")

    def stop_movement(self):
        if not self.running:
            return

        self.running = False
        self.status_label.config(text="Inactive", fg="gray")
        self.start_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED)

        # Show stopping notification
        self.show_notification("Cursor movement stopped",
                              "Cursor will no longer move")

    def move_cursor_loop(self):
        """Loop that moves cursor to random positions"""
        print(f"Cursor movement started with interval: {self.interval} seconds")

        while self.running:
            try:
                # Wait before moving (so first movement happens after interval)
                time.sleep(self.interval)

                # Check if still running (in case user clicked stop during wait)
                if not self.running:
                    break

                # Generate random coordinates
                x = random.randint(0, self.screen_width - 1)
                y = random.randint(0, self.screen_height - 1)

                print(f"Moving cursor to: ({x}, {y})")

                # Move cursor to random position
                pyautogui.moveTo(x, y, duration=0.1)

                print(f"Moved cursor to: ({x}, {y})")

            except Exception as e:
                print(f"Error in cursor movement: {e}")
                traceback.print_exc()
                break

        print("Cursor movement stopped")

    def show_notification(self, title, message):
        """Show system notification"""
        try:
            # Try to show native notification
            if sys.platform == "darwin":  # macOS
                osascript = f'''osascript -e 'display notification "{message}" with title "{title}"' '''
                import subprocess
                subprocess.run(osascript, shell=True)
            elif sys.platform.startswith("linux"):  # Linux
                # Try to use notify-send
                import subprocess
                subprocess.run(['notify-send', title, message],
                            stderr=subprocess.DEVNULL)
            # Windows notifications require additional libraries
        except Exception as e:
            print(f"Could not show notification: {e}")

    def on_closing(self):
        """Handle window closing"""
        if self.running:
            self.stop_movement()
            time.sleep(0.5)  # Give thread time to stop

        self.root.destroy()
        sys.exit(0)


def main():
    # Check if running from PyInstaller bundle
    if getattr(sys, 'frozen', False):
        print("Running in bundled mode")
    else:
        print("Running in development mode")

    # Create and run app
    root = Tk()

    # Force app to appear in foreground
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(lambda: root.attributes('-topmost', False))

    app = CursorMoverApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()

