import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pymavlink import mavutil
from Servo_example import ServoController, Servo

class ServoUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Servo Control")
        self.status_var = tk.StringVar(value="Disconnected")
        self.connection = None
        self.servo_config = None

        ttk.Label(root, text="Status:").grid(row=0, column=0)
        ttk.Label(root, textvariable=self.status_var, foreground="red").grid(row=0, column=1)

        ttk.Label(root, text="Angle (°):").grid(row=1, column=0)
        self.angle_entry = ttk.Entry(root)
        self.angle_entry.grid(row=1, column=1)

        ttk.Button(root, text="Send", command=self.send_angle).grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(root, text="Connect", command=self.connect).grid(row=3, column=0, columnspan=2)

    def connect(self):
        def task():
            try:
                self.connection = mavutil.mavlink_connection('udp:0.0.0.0:14550')
                self.connection.wait_heartbeat()
                self.servo_config = ServoConfiguration(self.connection)
                self.servo_config.writeServoParams()
                self.status_var.set("Connected")
            except Exception as e:
                self.status_var.set("Failed")
                messagebox.showerror("Connection Error", str(e))
        threading.Thread(target=task, daemon=True).start()

    def send_angle(self):
        if not self.servo_config:
            messagebox.showwarning("Not connected", "Connect first.")
            return
        try:
            angle = float(self.angle_entry.get())
            self.servo_config.sendAngle(angle)
        except Exception as e:
            messagebox.showerror("Send Error", str(e))

def main():
    root = tk.Tk()
    ServoUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
