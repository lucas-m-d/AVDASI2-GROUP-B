
from pymavlink import mavutil
import time

global connection_status
connection_status = "disconnected"

def connect_to_cube():
    print("Connecting to CubePilot...")
    mav = mavutil.mavlink_connection('udp:0.0.0.0:14550')
    return mav

def wait_heartbeat(mav):
    print("Waiting for heartbeat...")
    mav.wait_heartbeat()
    print(f"Heartbeat received from system {mav.target_system}, component {mav.target_component}")
    global connection_status
    connection_status = "connected"
    print("Status: connected")

def listen_messages(mav): 
    global connection_status
    last_msg_time = time.time()
    timeout = 10  # seconds to consider connection lost

    while True:
        msg = mav.recv_match(type=['SYS_STATUS'], timeout=1)
        if msg:
            print(f"Received: {msg.get_type()} - {msg.to_dict()}")
            last_msg_time = time.time()
            if connection_status != "connected":
                connection_status = "connected"
        else:
            # No message received in this interval
            if time.time() - last_msg_time > timeout:
                if connection_status != "disconnected":
                    print("Connection lost. Status: disconnected")
                connection_status = "disconnected"
        time.sleep(1)

if __name__ == "__main__":
    mav = connect_to_cube()
    wait_heartbeat(mav)
    listen_messages(mav)
