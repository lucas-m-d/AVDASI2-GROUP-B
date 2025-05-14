import asyncio
import threading
import tkinter as tk

from GS_example import connect_to_cube, wait_heartbeat, listen_messages
from Servo_example import ServoController, Servo
from UI_example import ServoUI  # UI logic imported here

# Async setup for MAVLink connection and message listening
async def setup_mav():
    mav = connect_to_cube()
    await wait_heartbeat(mav)

    servo_config = ServoController(mav)
    servo_config.writeServoParams()

    # Start listening to messages in background
    asyncio.create_task(listen_messages(mav))

    return servo_config

# Function to run Tkinter UI and the asyncio loop
def start_tk(loop):
    # Run MAV setup in the async loop
    loop.create_task(setup_mav())

    # Launch UI in the main thread
    root = tk.Tk()
    app = ServoUI(root)  # Only pass root if loop is handled internally in the UI
    app.loop = loop  # Optionally assign loop as an attribute if necessary
    root.mainloop()

# Main program that launches the event loop and Tkinter UI
def main():
    loop = asyncio.get_event_loop()  # Use the existing event loop

    # Start Tkinter UI in a separate thread
    threading.Thread(target=start_tk, args=(loop,)).start()

    # Run the event loop to handle background tasks (listening to messages, etc.)
    loop.run_forever()

if __name__ == "__main__":
    main()
