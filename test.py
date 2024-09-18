import ctypes
import time
import threading
import winsound
# Constants for MessageBox and MessageBeep
MB_OK = 0x00000000
MB_ICONINFORMATION = 0x00000040
MB_SYSTEMMODAL = 0x00001000
MB_ICONEXCLAMATION = 0x00000030
IDOK = 1

# Function to produce a hardware beep sound
def hardware_beep():
    winsound.Beep(2440,800)

# Function to start beeping until the user confirms
def start_beeping_until_confirm():
    confirmed = False

    def beep():
        nonlocal confirmed
        while not confirmed:
            hardware_beep()
            time.sleep(0.2)

    beeping_thread = threading.Thread(target=beep)
    beeping_thread.start()

    # Display a message box for user confirmation
    response = ctypes.windll.user32.MessageBoxW(
        0,
        "Internet is back. Click OK to stop the beep.",
        "Notification",
        MB_OK | MB_ICONINFORMATION | MB_SYSTEMMODAL
    )
    
    if response == IDOK:
        confirmed = True
        beeping_thread.join()

if __name__ == "__main__":
    # This block is to test the message box and beep functionality
    print("Testing MessageBox and beep...")
    start_beeping_until_confirm()
    print("MessageBox and beep test completed.")