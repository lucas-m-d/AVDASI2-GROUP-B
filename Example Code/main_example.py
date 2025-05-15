import tkinter as tk

import GS_example
import Servo_example
import UI_example

def setup_mav():
    mav = GS_example.connect_to_cube()
    if mav is None:
        # No connection, return None
        return None
    GS_example.wait_heartbeat(mav)
    servo_config = Servo_example.ServoController(mav)
    servo_config.write_servo_params()
    return servo_config

def main():
    # Start Tkinter in main thread
    root = tk.Tk()

    # Set up MAV and assign servo config (may be None)
    servo_config = setup_mav()
    app = UI_example.ServoUI(root, servo_config)  # Pass servo_config (can be None)

    root.mainloop()

if __name__ == "__main__":
    main()