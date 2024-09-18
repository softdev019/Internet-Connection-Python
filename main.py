import os
import time
import threading
import ctypes
from pystray import Icon, MenuItem as Item, Menu
from PIL import Image
from win10toast import ToastNotifier
from ping3 import ping
import winsound
# Paths to the tray icons
ICON_PATH_CONNECTED = "connect.ico"
ICON_PATH_DISCONNECTED = "disconnect.ico"

# Global variable to keep track of the internet connection status
connected = False
beeping_thread = None

# Constants for MessageBox and MessageBeep
MB_OK = 0x00000000
MB_ICONINFORMATION = 0x00000040
MB_SYSTEMMODAL = 0x00001000
MB_ICONEXCLAMATION = 0x00000030

# Function to create the tray icon
def create_tray_icon():
    icon = Icon('internet_monitor', Image.open(ICON_PATH_DISCONNECTED), "Internet Monitor", Menu(
        Item('Exit', exit_app)
    ))
    icon.run()

# Function to update the tray icon
def update_tray_icon(icon, connected):
    icon.icon = Image.open(ICON_PATH_CONNECTED if connected else ICON_PATH_DISCONNECTED)
    icon.visible = True

# Function to check the internet connection
def check_internet(icon):
    global connected, beeping_thread
    while True:
        try:
            response = ping('8.8.8.8')  # Google's public DNS server
            if response is None:
                if connected:
                    connected = False
                    notify_disconnection()
                    update_tray_icon(icon, connected)
            else:
                if not connected:
                    connected = True
                    notify_reconnection()
                    update_tray_icon(icon, connected)
        except Exception as e:
            print(f"Error checking internet connection: {e}")
        time.sleep(3)  # Check every 3 seconds

# Function to notify internet disconnection
def notify_disconnection():
    print("disconnect1")
    toaster = ToastNotifier()
    toaster.show_toast("Internet Disconnected", "The internet connection is lost.", duration=5)
    print("disconnect2")
    

# Function to notify internet reconnection with beep
def notify_reconnection():
    toaster = ToastNotifier()
    toaster.show_toast("Internet Reconnected", "The internet connection is back.", duration=5)
    start_beeping_until_confirm()

# Function to produce a hardware beep sound
def hardware_beep():
    ctypes.windll.user32.MessageBeep(MB_ICONEXCLAMATION)

# Function to start beeping until the user confirms
def start_beeping_until_confirm():
    global beeping_thread
    confirmed = False

    def beep():
        nonlocal confirmed
        while not confirmed:
            hardware_beep()
            time.sleep(1)

    beeping_thread = threading.Thread(target=beep)
    beeping_thread.start()

    # Display a message box for user confirmation
    response = ctypes.windll.user32.MessageBoxW(
        0,
        "Internet is back. Click OK to stop the beep.",
        "Notification",
        1 | MB_ICONINFORMATION | MB_SYSTEMMODAL
    )
    
    if response == 1:  # IDOK is 1
        confirmed = True
        beeping_thread.join()

# Function to exit the application
def exit_app(icon, item):
    icon.stop()
    os._exit(0)

if __name__ == "__main__":
    tray_icon = Icon('internet_monitor', Image.open(ICON_PATH_DISCONNECTED), "Internet Monitor", Menu(
        Item('Exit', exit_app)
    ))
    tray_icon_thread = threading.Thread(target=tray_icon.run)
    tray_icon_thread.daemon = True
    tray_icon_thread.start()

    # Initial connection status check
    initial_connected = ping('8.8.8.8') is not None
    connected = initial_connected
    update_tray_icon(tray_icon, connected)

    # Start checking internet connection
    check_internet(tray_icon)
