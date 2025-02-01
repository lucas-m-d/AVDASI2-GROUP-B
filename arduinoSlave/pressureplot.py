import numpy as np
import matplotlib.pyplot as plt
import socketio

# Initialize socket client
sio = socketio.Client()

# Arrays to hold pressure data and calculated coefficients
pressure_data = []
coefficients = []

# Constants
P_max = 400  # Adjust as needed
P_min = 0    # Adjust as needed

# Function to handle incoming data from CubePilot (via WebSocket)
@sio.event
def connect():
    print("Connected to CubePilot")

@sio.event
def disconnect():
    print("Disconnected from CubePilot")

@sio.event
def pressureData(data):
    """
    Process incoming pressure data from CubePilot.
    Data format should be a list of pressure readings.
    """
    global pressure_data, coefficients
    
    # Assuming data is a list of pressure sensor readings
    pressures = np.array(data)

    # Calculate pressure in Pascals using the given formula
    pressure_values = 1000 * ((5 / 1023) * pressures - 2.5)
    pressure_data = np.append(pressure_data, pressure_values)

    # Calculate coefficients using the provided formula
    coeffs = pressure_values / ((1.225 * 50 ** 2) / 2)
    coefficients = np.append(coefficients, coeffs)

    # Plot the pressure data and coefficients
    plot_data()

def plot_data():
    """
    Plot the pressure data and coefficients using matplotlib.
    """
    plt.figure(figsize=(10, 6))
    
    # Plot Pressure Data
    plt.subplot(2, 1, 1)
    plt.plot(pressure_data, color='red', label='Pressure Data')
    plt.title('Pressure Sensor Data')
    plt.xlabel('Sensor Reading Index')
    plt.ylabel('Pressure (Pa)')
    plt.legend()
    
    # Plot Coefficients
    plt.subplot(2, 1, 2)
    plt.plot(coefficients, color='blue', label='Coefficients')
    plt.title('Calculated Coefficients')
    plt.xlabel('Sensor Reading Index')
    plt.ylabel('Coefficient Value')
    plt.legend()
    
    plt.tight_layout()
    plt.pause(0.1)  # This allows the plot to update in real-time

def main():
    # Connect to the WebSocket server (your GCS)
    sio.connect("ws://your-gcs-server-address")

    # Run the plotting in a loop
    plt.ion()  # Interactive mode on
    plt.show()
    try:
        while True:
            pass  # Keep the loop running to receive data and plot in real-time
    except KeyboardInterrupt:
        print("Program terminated.")
        sio.disconnect()

if __name__ == '__main__':
    main()
