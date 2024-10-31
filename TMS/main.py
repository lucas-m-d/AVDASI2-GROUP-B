import asyncio
import pymavlink
import json
import websockets
from fetch.fetch import fetch
from requests.handler import handler
PORT = 8000

async def websocket_handler(websocket, path):
    """Main handler for each connected client."""
    # Create a task to send messages continuously
    send_task = asyncio.create_task(fetch(websocket))
    
    try:
        async for message in websocket:
            await handler(message)  # Handle incoming requests
    except websockets.ConnectionClosed:
        print("Connection closed")
    finally:
        send_task.cancel()  # Cancel the sending task if the connection closes
        
async def main():
    async with websockets.serve(websocket_handler, "localhost", PORT):
        await asyncio.Future()  # Run forever
    

asyncio.run(main())