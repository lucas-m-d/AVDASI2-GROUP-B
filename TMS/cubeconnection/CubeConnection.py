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

        self.testing = testing
        self.refresh = 1;       

        # set up a connection here to the cubepilot
        if not testing:
            self.connection = mavutil.mavlink_connection(connection_string)
            print("connecting...")
            self.connection.wait_heartbeat()
            print("Connection: Heartbeat from system (system %u component %u)" % (self.connection.target_system, self.connection.target_component))

            self.connection.system_time_send()

        else:
            print("testing data")
            
        self.time = time.time()
        self.csvfile = "cubelog.csv"
       

    def __testingGenerateData(self):
        data = {
            "time_boot_ms" : (time.time() - self.time)*1000,
            "roll" : random.uniform(-math.pi/4, math.pi/4),
            "pitch" : random.uniform(-math.pi/4, math.pi/4),
            "yaw" : random.uniform(-math.pi, math.pi)   
        }
        
        return data

    def __updateStatus(self): # check whether needs to be asynchronous
        '''Function to continually update data and return the data'''
        '''May not even need'''

        data = []
        if not self.testing:
            for i in self.req_data:
                data.append(self.connection.recv_match(type=i, blocking=True).to_dict()) ## perhaps use a dictionary to get required most recent values from self.connection.messages
        else:
            data = self.__testingGenerateData()
        print(data)
        return data

    async def fetch(self, websocket):
        '''take returned data from updateStatus and then send to the websocket'''
        while True:
            data = self.__updateStatus()
            print(data)
            await websocket.send(json.dumps(data))
            await asyncio.sleep(self.refresh) ## do we need this?   

            
        

        
        