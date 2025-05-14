#Example code to connect to CubePilot throuogh wifi and listen for messages
#Written by: Ethan Sheehan



import asyncio #runs asyncronous tasks
from pymavlink import mavutil #Mavlink library for communication with CubePilot

# Connect to CubePilot
mav = mavutil.mavlink_connection('udp:0.0.0.0:14550')

#Wait for heartbeat from cube
async def wait_heartbeat():
    print("Waiting for heartbeat...")
    mav.wait_heartbeat()
    print(f"Heartbeat received from system {mav.target_system}, component {mav.target_component}") #Print when heartbeat is received

#Listen for messages from cube
async def listen_messages(): 
    while True:
        msg = mav.recv_match(type=['SYS_STATUS']) #Defiine message type
        if msg:
            print(f"Received: {msg.get_type()} - {msg.to_dict()}") #Print message
        await asyncio.sleep(5) #Wait 5 seconds

async def main():
    await wait_heartbeat()

    # Start listening to messages
    asyncio.create_task(listen_messages())

    # Keep running to listen to messages
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
