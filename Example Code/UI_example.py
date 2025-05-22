##########################################
#UI example python script for AVDASI 2 AVIONICS
#Creates a barebones UI for your GS
#shows connections status
#Arming button
#Safety switch toggle button
#Set servo angle
#Author: Ethan Sheehan

#This file should be able to run independently
#Potential upgrades:
    #Make it actually look good
    #Allow multiple servos simulatneously
    #Mode switching
    #Flap position
    #Flap angle graph
    #Live data graphing
    #Use another module/code to make it look better (tkinter has its limits)
    #Make it run faster/smoother/better response time

##########################################

import tkinter as tk
from tkinter import ttk, messagebox

#Call other example codes
import Servo_example
import GS_example
import Arm_example

#Class for Servo UI functions
class ServoUI:
    #How the UI looks function
    def __init__(self, root, servo_config=None):
        #Initialize the main window and store the servo configuration
        self.root = root
        self.root.title("Servo Control")
        self.servo_config = servo_config

        #Connection status display
        self.status_var = tk.StringVar(value=GS_example.connection_status.capitalize())
        ttk.Label(root, text="Status:").grid(row=0, column=0)
        ttk.Label(root, textvariable=self.status_var, foreground="red").grid(row=0, column=1)

        #Entry field for angle input
        ttk.Label(root, text="Angle (°):").grid(row=1, column=0)
        self.angle_entry = ttk.Entry(root)
        self.angle_entry.grid(row=1, column=1)

        #Button to send the angle to the servo
        ttk.Button(root, text="Send", command=self.send_angle).grid(row=2, column=0, columnspan=2, pady=5)

        #Safety switch button
        self.safety_enabled = True
        self.safety_button = ttk.Button(
            root,
            text="Safety Enabled (Click to toggle)" if self.safety_enabled else "Safety Disabled (Click to toggle)",
            command=self.toggle_safety
        )
        self.safety_button.grid(row=3, column=0, columnspan=2, pady=5)

        #Arming button
        self.armed = False
        self.arming_button = ttk.Button(
            root,
            text="Arming Disabled (Click to toggle)",
            command=self.toggle_arming
        )
        self.arming_button.grid(row=4, column=0, columnspan=2, pady=5)

        #Arming status label
        self.arming_status_label = ttk.Label(
            root,
            text="DISARMED - NO LOGGING",
            background="red",
            foreground="white"
        )
        self.arming_status_label.grid(row=5, column=0, columnspan=2, pady=5)

        #Start status updater loop
        self.update_status()

    #safety switch action function
    def toggle_safety(self):
        #Toggles the safety switch state on the flight controller
        if not self.servo_config:
            messagebox.showwarning("Not connected", "Connect first.")
            return
        mav = self.servo_config.mav
        #Toggle the state
        new_state = not self.safety_enabled
        success = Arm_example.toggle_safety_switch(mav, new_state) #calls arming example code
        #Update button text based on new state
        if success:
            self.safety_enabled = new_state
            if self.safety_enabled:
                self.safety_button.config(text="Safety Enabled (Click to toggle)")
            else:
                self.safety_button.config(text="Safety Disabled (Click to toggle)")
        else:
            messagebox.showerror("Safety Switch", "Failed to toggle safety switch.")

    #arming action function
    def toggle_arming(self):
        #Toggles the arming state of the vehicle
        if not self.servo_config:
            messagebox.showwarning("Not connected", "Connect first.")
            return
        mav = self.servo_config.mav
        self.armed = not self.armed
        success = Arm_example.toggle_arming_switch(mav, self.armed) #calls arming example code
        if success:
            if self.armed:
                self.arming_button.config(text="Arming Enabled (Click to toggle)")
                self.arming_status_label.config(text="ARMED AND LOGGING", background="green", foreground="white")
            else:
                self.arming_button.config(text="Arming Disabled (Click to toggle)")
                self.arming_status_label.config(text="DISARMED - NO LOGGING", background="red", foreground="white")

    #connection status action function
    def update_status(self):
        #Updates the connection status label every 1000 miliseconds
        self.status_var.set(GS_example.connection_status.capitalize()) #call GS example code
        self.root.after(1000, self.update_status)

    #servo configuration function
    def set_servo_controller(self, servo_config):
        self.servo_config = servo_config #writes servo configuration

    #servo angle action function
    def send_angle(self):
        #Sends angle value entered by the user to the servo
        if not self.servo_config: #check if connected
            messagebox.showwarning("Not connected", "Connect first.")
            return
        try:
            angle = float(self.angle_entry.get()) #Get angle from input
            self.servo_config.send_angle(angle) #Send angle via MAVLink
        except Exception as e: #error handling
            messagebox.showerror("Send Error", str(e))

#Independence call
if __name__ == "__main__":#allows this script to be ran independently
    #can be used to test if it works before integrating into wider system
    #useful for debugging
    root = tk.Tk() #Creates the main application window for the UI using Tkinter
    servo_config = None
    try:
        #Attempt to connect to the servo controller
        servo_config = Servo_example.ServoController()  #Adjust class name
    except Exception as e: #error handling
        messagebox.showwarning("Connection Error", f"Could not connect to servo: {e}")
        servo_config = None

    #Launch the Servo UI
    servo_ui = ServoUI(root, servo_config)
    root.mainloop()
