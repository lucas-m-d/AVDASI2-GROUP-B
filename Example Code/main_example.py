import asyncio
import threading
import tkinter as tk

from GS_example import connect_to_cube, wait_heartbeat, listen_messages
from Servo_example import ServoController
from UI_example import ServoUI


# Async setup for MAVLink connection and message listening
async def setup_mav():

    servo_config = ServoController(mav)

    asyncio.create_task(listen_messages(mav))
    return servo_config


def start_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def main():
    loop = asyncio.new_event_loop()

    # Start asyncio loop in background
    threading.Thread(target=start_asyncio_loop, args=(loop,), daemon=True).start()

    # Start Tkinter in main thread
    root = tk.Tk()
    app = ServoUI(root, loop)  # Pass loop as expected

    # Set up MAV and assign servo config after connection
    async def init():
        servo_config = await setup_mav()
        app.set_servo_controller(servo_config)

    asyncio.run_coroutine_threadsafe(init(), loop)
    root.mainloop()


if __name__ == "__main__":
    main()
