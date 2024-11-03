import asyncio
import pymavlink
import json
import websockets
from fetch.fetch import fetch
from requests.handler import handler
from cubeconnection.CubeConnection import CubeConnection
PORT = 8000

con = CubeConnection('tcpin:localhost:14553', testing=True)

print("here")


async def websocket_loop(websocket, path):
    """Main handler for each connected client."""
    # Create a task to send messages continuously
    send_task = asyncio.create_task(con.fetch(websocket))
    #send_task_2 = asyncio.create_task(fetch(websocket))
    
    try:
        async for message in websocket:
            await handler(message)  # Handle incoming requests

    except websockets.ConnectionClosed:
        print("Connection closed")

    finally:
        send_task.cancel()  # Cancel the sending task if the connection closes
        
async def main():
    async with websockets.serve(websocket_loop, "localhost", PORT):
        await asyncio.Future()  # Run forever
    

asyncio.run(main())