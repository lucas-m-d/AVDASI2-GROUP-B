import asyncio
import json

REFRESH = 0.1
### fetch data from UAV however it needs to be done
async def getData():
    drone_data = {
        "altitude": 1200,  # Replace with actual drone data
        "speed": 30,       # Replace with actual drone data
        "battery": 75      # Replace with actual drone data
    }
    return drone_data

## send to socket

async def fetch(websocket):
    while True:
        data = await getData()
        await websocket.send(json.dumps(data))
        await asyncio.sleep(REFRESH)

    

 