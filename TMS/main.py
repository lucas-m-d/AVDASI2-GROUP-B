import asyncio
import pymavlink
import json
import websockets
from cubeconnection.CubeConnection import CubeConnection, FlightMode
PORT = 8001
#udp:0.0.0.0:14550
con = CubeConnection('com6', testing=False) ## connection string on left - can change

#con._set_mode(FlightMode.MANUAL)

#print(con.connection.recv_match(type="HIGH_LATENCY2", blocking=True).to_dict())
##### todo: make it send a websocket on heartbeat received

async def websocket_loop(websocket, path):
    """Main handler for each connected client."""
    # Create a task to send messages continuously
    send_task = asyncio.create_task(con.update(websocket))
    
    try:
        async for message in websocket:
            await con.handle(message)  # Handle incoming requests

    except websockets.ConnectionClosed:
        print("Connection closed")

    finally:
        send_task.cancel()  # Cancel the sending task if the connection closes
        
async def main():
    async with websockets.serve(websocket_loop, "localhost", PORT):
        await asyncio.Future()  # Run forever
    

asyncio.run(main())