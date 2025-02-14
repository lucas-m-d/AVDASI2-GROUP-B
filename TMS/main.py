import asyncio
import json
import websockets
from cubeconnection.CubeConnection import CubeConnection

PORT = 8001
CONSTR = 'udp:0.0.0.0:14550' # use this for UDP connection
#CONSTR = 'com6'




##con = asyncio.create_task(CubeConnection(CONSTR, testing=TEST))
#### pass websocket into connection?

#con._set_mode(FlightMode.MANUAL)

#print(con.connection.recv_match(type="HIGH_LATENCY2", blocking=True).to_dict())
##### todo: make it send a websocket on heartbeat received


        
async def main():
    con = CubeConnection(CONSTR)
    asyncio.create_task(con.init())

    async def websocket_handler(websocket, path):
        
        await con.update(websocket=websocket)
        
        try:
            async for message in websocket:
                await con.handle(message)  # Handle incoming requests

        except websockets.ConnectionClosed:
            print("Connection closed")
        
        finally:
            con.messageLoop() ## keep running message loop without websocket



    async with websockets.serve(websocket_handler, "localhost", PORT):
        await asyncio.Future()  # Run forever
    

asyncio.run(main())