import asyncio
import pymavlink
import json
import websockets
from cubeconnection.CubeConnection import CubeConnection, FlightMode
PORT = 8001
CONSTR = 'udp:0.0.0.0:14550' # use this for UDP connection
TEST = False


##con = asyncio.create_task(CubeConnection(CONSTR, testing=TEST))
#### pass websocket into connection?

#con._set_mode(FlightMode.MANUAL)

#print(con.connection.recv_match(type="HIGH_LATENCY2", blocking=True).to_dict())
##### todo: make it send a websocket on heartbeat received


        
async def main():
    con = CubeConnection(CONSTR, testing=TEST)
    asyncio.create_task(con.init())


    async def websocket_handler(websocket, path):
        """Main handler for each connected client."""
        while not con.initialised:
            await websocket.send(json.dumps({
                "type":"ERROR",
                "ERROR":0
            }))
            await asyncio.sleep(2)
        else:
            send_task = websocket.send(
                {
                    "type":"HEARTBEAT",
                    "error":0
                }
            )
        
        try:
            async for message in websocket:
                await con.handle(message)  # Handle incoming requests

        except websockets.ConnectionClosed:
            print("Connection closed")

        # finally:
        #     send_task.cancel()  # Cancel the sending task if the connection closes

    async with websockets.serve(websocket_handler, "localhost", PORT):
        await asyncio.Future()  # Run forever
    

asyncio.run(main())