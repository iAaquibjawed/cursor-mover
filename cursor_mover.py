#!/usr/bin/env python3
"""
macOS Menu Bar Random Cursor Mover
A native status bar application using rumps
"""

import rumps
import pyautogui
import random
import threading
import time
import subprocess

pyautogui.FAILSAFE = False


class CursorMoverApp(rumps.App):
    def __init__(self):
        super(CursorMoverApp, self).__init__(
            "Cursor Mover",
            icon=None,
            quit_button=None
        )
        self.title = "🖱️"

        # State variables
        self.running = False
        self.interval = 11
        self.thread = None
        self.movement_lock = threading.Lock()

        try:
            self.screen_width, self.screen_height = pyautogui.size()
        except Exception:
            self.screen_width, self.screen_height = (1920, 1080)

        # Build menu with keyboard shortcuts
        self.menu = [
            rumps.MenuItem("Status: 🔴 Inactive", callback=None),
            rumps.separator,
            rumps.MenuItem(f"Current Interval: {self.interval}s", callback=None),
            rumps.MenuItem("⚙️ Change Interval...", callback=self.set_interval, key='i'),
            rumps.separator,
            rumps.MenuItem("Start Movement", callback=self.toggle_movement, key='s'),
            rumps.separator,
            rumps.MenuItem(f"Screen: {self.screen_width}×{self.screen_height}", callback=None),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_app, key='q')
        ]

        self.status_item = self.menu["Status: 🔴 Inactive"]
        self.interval_display = self.menu[f"Current Interval: {self.interval}s"]
        self.interval_button = self.menu["⚙️ Change Interval..."]
        self.toggle_item = self.menu["Start Movement"]
        self.screen_item = self.menu[f"Screen: {self.screen_width}×{self.screen_height}"]

    def set_interval(self, sender):
        """Open dialog to set movement interval using AppleScript"""
        def show_dialog():
            try:
                # Use AppleScript to show a text input dialog and get the result
                script = f'''
                set userResponse to display dialog "Enter interval in seconds (minimum 10):" & return & return default answer "{self.interval}" with title "Set Interval" buttons {{"Cancel", "Set"}} default button 2
                set buttonPressed to button returned of userResponse
                set textEntered to text returned of userResponse
                return buttonPressed & "|||" & textEntered
                '''
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    # Parse the result
                    output = result.stdout.strip()
                    if "|||" in output:
                        button, text = output.split("|||", 1)
                        if button.strip() == "Set":
                            try:
                                new_interval = int(text.strip())
                                if new_interval < 10:
                                    # Show error using alert
                                    error_script = 'display dialog "Interval must be at least 10 seconds." buttons {{"OK"}} default button 1 with title "Invalid Interval"'
                                    subprocess.run(['osascript', '-e', error_script], check=False)
                                    return

                                if new_interval != self.interval:
                                    old_interval = self.interval
                                    self.interval = new_interval
                                    self.interval_display.title = f"Current Interval: {self.interval}s"

                                    self.safe_notification(
                                        title="Cursor Mover",
                                        subtitle="Interval Updated",
                                        message=f"Changed from {old_interval}s to {self.interval}s"
                                    )
                            except ValueError:
                                # Show error using alert
                                error_script = 'display dialog "Please enter a valid number." buttons {{"OK"}} default button 1 with title "Invalid Input"'
                                subprocess.run(['osascript', '-e', error_script], check=False)
            except subprocess.TimeoutExpired:
                pass  # User didn't respond
            except Exception as e:
                print(f"Dialog error: {e}")

        # Run dialog without blocking
        dialog_thread = threading.Thread(target=show_dialog, daemon=True)
        dialog_thread.start()

    def safe_notification(self, title, subtitle, message):
        """Send notification using native macOS notification system"""
        # First try rumps notification
        try:
            rumps.notification(title=title, subtitle=subtitle, message=message)
        except RuntimeError:
            # If that fails, use AppleScript for native notifications
            script = f'''
            display notification "{message}" with title "{title}" subtitle "{subtitle}"
            '''
            try:
                subprocess.run(['osascript', '-e', script], check=False, capture_output=True)
            except Exception:
                print(f"[Notification] {title}: {subtitle} - {message}")

    def toggle_movement(self, sender):
        """Start or stop cursor movement"""
        if not self.running:
            self.start_movement()
        else:
            self.stop_movement()

    def start_movement(self):
        """Start the cursor movement loop"""
        # Check if we have accessibility permissions
        try:
            _ = pyautogui.position()
        except Exception:
            rumps.alert(
                "Permission Required",
                "Cursor Mover needs Accessibility permission.\n\n"
                "Go to: System Settings → Privacy & Security → Accessibility\n"
                "Enable 'Python' or your terminal application."
            )
            return

        with self.movement_lock:
            if self.running:
                return

            self.running = True
            self.update_ui_state(active=True)

            # Start movement thread
            self.thread = threading.Thread(target=self.move_cursor_loop, daemon=True)
            self.thread.start()

            self.safe_notification(
                title="Cursor Mover",
                subtitle="Movement Started",
                message=f"Moving cursor every {self.interval} seconds"
            )

    def stop_movement(self):
        """Stop the cursor movement loop"""
        with self.movement_lock:
            if not self.running:
                return

            self.running = False
            self.update_ui_state(active=False)

            self.safe_notification(
                title="Cursor Mover",
                subtitle="Movement Stopped",
                message="Cursor movement has been stopped"
            )

    def update_ui_state(self, active: bool):
        """Update menu items based on active state"""
        if active:
            self.status_item.title = "Status: 🟢 Active"
            self.toggle_item.title = "⏸ Stop Movement"
            # Keep icon as 🖱️ always
            self.title = "🖱️"
        else:
            self.status_item.title = "Status: 🔴 Inactive"
            self.toggle_item.title = "▶ Start Movement"
            self.title = "🖱️"

    def move_cursor_loop(self):
        """Background thread that moves cursor at intervals"""
        next_move_time = time.time() + self.interval

        while self.running:
            current_time = time.time()

            if current_time >= next_move_time:
                # Time to move cursor
                x = random.randint(0, self.screen_width - 1)
                y = random.randint(0, self.screen_height - 1)

                try:
                    pyautogui.moveTo(x, y, duration=0.25)
                    next_move_time = time.time() + self.interval
                except Exception as e:
                    print(f"Error moving cursor: {e}")
                    self.running = False
                    self.update_ui_state(active=False)
                    rumps.alert("Error", f"Failed to move cursor: {e}")
                    break

            # Sleep in small increments to check running flag frequently
            time.sleep(0.5)

    def quit_app(self, sender):
        """Clean quit handler"""
        if self.running:
            self.stop_movement()
        rumps.quit_application()


if __name__ == "__main__":
    app = CursorMoverApp()
    app.run()