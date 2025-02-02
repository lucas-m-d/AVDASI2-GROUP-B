import numpy as np
import random
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# Constants
density = 1.225  # kg/m^3

# Generate random PressureData between 300 and 600 (ADC range)
def generate_pressure_data():
    return np.random.randint(300, 601, size=12)

# Compute the coefficients of pressure (Cp)
def calculate_cp(PressureData, Speed):
    # PressureData is raw ADC values, converting to pressure (in Pa)
    PressureData = 100 * ((PressureData * (5 / 1023)) - 2.5)
    # Calculate Cp using Speed
    Cp_values = PressureData / ((density * (Speed ** 2)) / 2)
    return Cp_values

# Initialize the Tkinter root window
root = tk.Tk()
root.title("Cp vs Sensor Number")

# Set the size of the Tkinter window
root.geometry("1000x600")

# Frame for the speed input
speed_frame = tk.Frame(root)
speed_frame.pack(pady=10)

# Label for the speed input
speed_label = tk.Label(speed_frame, text="Enter Speed (m/s):")
speed_label.pack(side=tk.LEFT, padx=5)

# Entry widget for speed
speed_entry = tk.Entry(speed_frame, width=10)
speed_entry.insert(0, "20")  # Default speed value
speed_entry.pack(side=tk.LEFT, padx=5)

# Get speed from the entry widget
def get_speed():
    try:
        speed_value = float(speed_entry.get())
    except ValueError:
        speed_value = 20  # Default speed if input is invalid
    return speed_value

# Generate sensor numbers for the x-axis (1 through 12)
sensor_numbers = np.arange(1, 13)

# Create the figure and axes for the plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_title('Cp vs Pressure Sensor Number')
ax.set_xlabel('Pressure Sensor Number')
ax.set_ylabel('Cp')
ax.grid(True)
ax.set_xlim(0, 13)  # X-axis limit (for 12 sensors)
ax.set_ylim(-0.5, 0.5)  # Y-axis limit

# Line object for the plot (connects the points)
line, = ax.plot([], [], 'r-', label="Cp values")  # Red line connecting points

# Scatter object for the crosses (points)
scatter, = ax.plot([], [], 'rx', label="Sensor Data")  # Red 'x' markers for each data point

# Create the canvas to embed the plot in the Tkinter window
canvas_frame = tk.Frame(root)
canvas_frame.pack(pady=10)

# Create a FigureCanvasTkAgg to embed the Matplotlib figure in Tkinter
canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.get_tk_widget().pack()

# Label to show the raw sensor values and Cp values
data_label = tk.Label(root, text="Sensor Data & Cp values will appear here", justify=tk.LEFT)
data_label.pack(pady=10)

# Update function for animation
def update(frame):
    speed_value = get_speed()

    # Generate random PressureData for 12 sensors (raw values between 300 and 600)
    PressureData = generate_pressure_data()

    # Update Cp values based on the current Speed
    Cp_values = calculate_cp(PressureData, speed_value)

    # Update the plot with new Cp values and connect them with lines
    line.set_data(sensor_numbers, Cp_values)

    # Update the scatter plot (crosses) with the individual data points
    scatter.set_data(sensor_numbers, Cp_values)

    # Update the data label with raw sensor values and Cp values
    data_str = "Sensor Number | Raw Sensor Value | Cp Value\n"
    for i in range(12):
        data_str += f"{sensor_numbers[i]} | {PressureData[i]} | {Cp_values[i]:.3f}\n"
    data_label.config(text=data_str)

    # Redraw the canvas
    canvas.draw()

    return line, scatter

# Function to start the animation
def start_animation():
    ani = FuncAnimation(fig, update, frames=100, interval=500, blit=True)  # interval for live updates

# Start the animation loop when the Tkinter window is opened
start_animation()

# Start the Tkinter event loop
root.mainloop()
