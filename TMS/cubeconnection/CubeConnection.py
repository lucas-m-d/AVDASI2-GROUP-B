from pymavlink import mavutil
import random
import time
import math
import asyncio
import json

class CubeConnection:
    def __init__(self, connection_string, testing=False):
        '''
        Required info from the mav
        '''

        self.req_data = ["ATTITUDE"]

        self.inputs = ["flaps"]

        self.testing = testing
        self.refresh = 1/3;       

        # set up a connection here to the cubepilot
        if not testing:
            self.connection = mavutil.mavlink_connection(connection_string)
            print("connecting...")
            self.connection.wait_heartbeat()
            print("Connection: Heartbeat from system (system %u component %u)" % (self.connection.target_system, self.connection.target_component))
            #self.connection.system_time_send()
            ## init a bunch of stuff

        else:
            print("testing data")
            
        self.time = time.time()
       

    def _testingGenerateData(self):
        data = {
            "time_boot_ms" : (time.time() - self.time)*1000,
            "roll" : random.uniform(-math.pi/4, math.pi/4),
            "pitch" : random.uniform(-math.pi/4, math.pi/4),
            "yaw" : random.uniform(-math.pi, math.pi)   
        }
        return data

    def _updateStatus(self): # check whether needs to be asynchronous
        '''Function to continually update data and return the data'''
        '''May not even need'''

        data = self.connection.recv_match(type="ATTITUDE", blocking=True).to_dict()
        # if not self.testing:
        #     for i in self.req_data:
        #         data.append(self.connection.recv_match(type=i, blocking=True).to_dict()) ## perhaps use a dictionary to get required most recent values from self.connection.messages
        if self.testing:
            data = self._testingGenerateData()
        #print(data)

        
        return {
            "time_boot_ms":data["time_boot_ms"],
            "roll":data["roll"],
            "pitch": (data["pitch"]*180 / math.pi),
            "yaw": data["yaw"]
        }
    
    def _sendFlapRequest(self, angle): ##todo
        print("requested angle:", angle)

        self.connection.mav.command_long_send(
        self.connection.target_system,
        self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            1,
            10,
            (1000 + angle * 1000 / 360 ),
            0,
            0,
            0,
            0,
            0
    )
        pass

    async def update(self, websocket):
        '''take returned data from updateStatus and then send to the websocket'''
        while True:
            #print("updating... ")
            data = self._updateStatus()
            #print(data)
            await websocket.send(json.dumps(data))
            await asyncio.sleep(self.refresh) ## do we need this?

    async def handle(self, message):
        print(message)
        if 'flaps' in message:
            self._sendFlapRequest(message['flaps'])
    

            
        

        
        
