import tkinter as tk
from tkinter import ttk, messagebox
import Servo_example
import GS_example
import Arm_example

class ServoUI:
    def __init__(self, root, servo_config=None):
        self.root = root
        self.root.title("Servo Control")
        self.servo_config = servo_config

        self.status_var = tk.StringVar(value=GS_example.connection_status.capitalize())

        ttk.Label(root, text="Status:").grid(row=0, column=0)
        ttk.Label(root, textvariable=self.status_var, foreground="red").grid(row=0, column=1)

        ttk.Label(root, text="Angle (°):").grid(row=1, column=0)
        self.angle_entry = ttk.Entry(root)
        self.angle_entry.grid(row=1, column=1)

        ttk.Button(root, text="Send", command=self.send_angle).grid(row=2, column=0, columnspan=2, pady=5)

        # Safety switch button
        self.safety_enabled = True
        self.safety_button = ttk.Button(
            root,
            text="Safety Enabled (Click to toggle)" if self.safety_enabled else "Safety Disabled (Click to toggle)",
            command=self.toggle_safety
        )
        self.safety_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Arming switch button
        self.armed = False
        self.arming_button = ttk.Button(
            root,
            text="Arming Disabled (Click to toggle)",
            command=self.toggle_arming
        )
        self.arming_button.grid(row=4, column=0, columnspan=2, pady=5)

        # Arming status label
        self.arming_status_label = ttk.Label(
            root,
            text="DISARMED - NO LOGGING",
            background="red",
            foreground="white"
        )
        self.arming_status_label.grid(row=5, column=0, columnspan=2, pady=5)

        self.update_status()

    def toggle_safety(self):
        if not self.servo_config:
            messagebox.showwarning("Not connected", "Connect first.")
            return
        mav = self.servo_config.mav
        # Toggle the state
        new_state = not self.safety_enabled
        success = Arm_example.toggle_safety_switch(mav, new_state)
        if success:
            self.safety_enabled = new_state
            if self.safety_enabled:
                self.safety_button.config(text="Safety Enabled (Click to toggle)")
            else:
                self.safety_button.config(text="Safety Disabled (Click to toggle)")
        else:
            messagebox.showerror("Safety Switch", "Failed to toggle safety switch.")

    def toggle_arming(self):
        if not self.servo_config:
            messagebox.showwarning("Not connected", "Connect first.")
            return
        mav = self.servo_config.mav
        self.armed = not self.armed
        success = Arm_example.toggle_arming_switch(mav, self.armed)
        if success:
            if self.armed:
                self.arming_button.config(text="Arming Enabled (Click to toggle)")
                self.arming_status_label.config(text="ARMED AND LOGGING", background="green", foreground="white")
            else:
                self.arming_button.config(text="Arming Disabled (Click to toggle)")
                self.arming_status_label.config(text="DISARMED - NO LOGGING", background="red", foreground="white")

    def update_status(self):
        self.status_var.set(GS_example.connection_status.capitalize())
        self.root.after(1000, self.update_status)

    def set_servo_controller(self, servo_config):
        self.servo_config = servo_config

    def send_angle(self):
        if not self.servo_config:
            messagebox.showwarning("Not connected", "Connect first.")
            return
        try:
            angle = float(self.angle_entry.get())
            self.servo_config.send_angle(angle)
        except Exception as e:
            messagebox.showerror("Send Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    servo_config = None
    try:
        # Attempt to connect to the servo controller if needed
        servo_config = Servo_example.ServoController()  # Adjust class name if needed
    except Exception as e:
        messagebox.showwarning("Connection Error", f"Could not connect to servo: {e}")
        servo_config = None

    servo_ui = ServoUI(root, servo_config)
    root.mainloop()
