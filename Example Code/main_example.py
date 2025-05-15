import tkinter as tk
import threading

import GS_example
import Servo_example
import UI_example

def setup_mav():
    mav = GS_example.connect_to_cube()
    if mav is None:
        # No connection, return None
        return None, None
    GS_example.wait_heartbeat(mav)
    servo_config = Servo_example.ServoController(mav)
    servo_config.write_servo_params()
    return servo_config, mav

def main():
    root = tk.Tk()

    # Set up MAV and assign servo config (may be None)
    servo_config, mav = setup_mav()
    app = UI_example.ServoUI(root, servo_config)  # Pass servo_config (can be None)

    # Start background listener if connected
    if mav is not None:
        threading.Thread(target=GS_example.listen_messages, args=(mav,), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()