# cube_connection.py

import asyncio
from pymavlink import mavutil

def connect_to_cube():
    print("Connecting to CubePilot...")
    mav = mavutil.mavlink_connection('udp:0.0.0.0:14550')
    return mav

async def wait_heartbeat(mav):
    print("Waiting for heartbeat...")
    mav.wait_heartbeat()
    print(f"Heartbeat received from system {mav.target_system}, component {mav.target_component}")

async def listen_messages(mav): 
    while True:
        msg = mav.recv_match(type=['SYS_STATUS'])
        if msg:
            print(f"Received: {msg.get_type()} - {msg.to_dict()}")
        await asyncio.sleep(5)
