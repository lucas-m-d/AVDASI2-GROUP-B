import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
from pymavlink import mavutil
from Servo_example import ServoController, Servo

class ServoUI:
    def __init__(self, root, loop, servo_config=None):
        self.root = root
        self.root.title("Servo Control")
        self.loop = loop  # <- Add loop for async execution
        self.status_var = tk.StringVar(value="Disconnected")
        self.connection = None
        self.servo_config = servo_config  # Can be passed externally or created via Connect button

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
                self.servo_config = ServoController(self.connection)
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
            # Properly run the coroutine
            asyncio.run_coroutine_threadsafe(
                self.servo_config.send_angle(angle),
                self.loop
            )
        except Exception as e:
            messagebox.showerror("Send Error", str(e))
