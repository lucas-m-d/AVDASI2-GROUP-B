from pymavlink import mavutil
import random
import time
import math
import asyncio
import json
from enum import Enum

class FlightMode(Enum):
    
    MANUAL = 0
    STABILISE = 2

class CubeConnection:
    def __init__(self, connection_string, testing=False):
        '''
        Required info from the mav
        '''

        self.req_data = ["ATTITUDE"]

        self.testing = testing
        self.refresh = 1/10
        
        self._latest_message_ID = 0       

        # set up a connection here to the cubepilot
        if not testing:
            self.connection = mavutil.mavlink_connection(connection_string, baud=111100)
            print("connecting...")

            
            #self.connection.wait_heartbeat()
            self.connection.wait_heartbeat()
            print("Connection: Heartbeat from system (system %u component %u)" % (self.connection.target_system, self.connection.target_component))

            #self.connection.system_time_send()
            ## init a bunch of stuff
            print(self.connection.recv_match(type="ATTITUDE", blocking=True).to_dict())
            #### configure cubepilot here
            #### code has gone missing !!!!!!!

            ## send attitude data at refresh rate
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                1,
                self.refresh,
                30,
                0,0,0,0,0
            )
            ## dismarm everything on load
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,
                1, 0, 0, 0, 0, 0, 0)
            
            self.flap_pins = [10]

            ## rc control
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                0,
                FlightMode.MANUAL.value,     ## manual=0, stabilize=2
                0, 0, 0, 0, 0, 0)
            self.send_rc_override([1500, 1500, 1500, 1500, 0,0,0,0])
        else:
            print("testing data")
            
        self.time = time.time()
       
    def _getLatestMessageID(self):
        self._latest_message_ID += 1
        return self._latest_message_ID - 1

    def _testingGenerateData(self):
        data = {
            "time_boot_ms" : (time.time() - self.time)*1000,
            "roll" : random.uniform(-math.pi/4, math.pi/4),
            "pitch" : random.uniform(-math.pi/4, math.pi/4),
            "yaw" : random.uniform(-math.pi, math.pi)   
        }
        return data

    async def _updateStatus(self): 
        '''Function to continually update data and return the data'''
        
        if not self.testing:
            data = self.connection.recv_match(type="ATTITUDE", blocking=True).to_dict() # get attitude info
            data2 = self.connection.recv_match(type="HEARTBEAT", blocking=True).to_dict()
        print(data2["custom_mode"])
    def _set_mode(self, mode):
        """
        Set the flight mode of the Cube.
        :param mode: FlightMode Enum (e.g., FlightMode.MANUAL or FlightMode.STABILISE)
        """
        try:
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                0,
                mode.value,
                0, 0, 0, 0, 0, 0
            )
            print(f"Flight mode set to {mode.name}")
        except Exception as e:
            print("Error setting flight mode:", e)

    def send_rc_override(self, channels):
        """
        Send MAVLink RC_OVERRIDE commands to override RC inputs.
        :param channels: List of 8 channel values (e.g., [1500, 1500, 1500, 1500, 0, 0, 0, 0])
        """
        try:
            self.connection.mav.rc_channels_override_send(
                self.connection.target_system,
                self.connection.target_component,
                *channels
            )
            print("RC_OVERRIDE sent:", channels)
        except Exception as e:
            print("Error sending RC_OVERRIDE:", e)

    def clear_rc_override(self):
        """
        Clear MAVLink RC_OVERRIDE to revert control to the RC transmitter.
        """
        self.send_rc_override([0, 0, 0, 0, 0, 0, 0, 0])
        print("RC_OVERRIDE cleared.")


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
        servo_max_pos = 90
        pwm_command = 1000 + (angle * 2000 / servo_max_pos)
        print(pwm_command)
        if not self.testing:
            try:
                
                self.connection.mav.command_long_send(
                    self.connection.target_system,
                    self.connection.target_component,
                        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
                        1,
                        10,
                        (pwm_command),
                        0,
                        0,
                        0,
                        0,
                        0
                )
                print("pwn_command")   
                    
            except Exception as e:
                print("error sending flap request message")
                print(e)
        pass
    
    def _sendArmRequest(self, arm):
        req = 0
        if arm:
            req = 1
        try:
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                self._getLatestMessageID(),
            req, 0, 0, 0, 0, 0, 0)

                
        except Exception as e:
            print("error sending arm request message")
            print(e)

    async def update(self, websocket):
        '''take returned data from updateStatus and then send to the websocket'''
        while True:
            #print("updating... ")
            data = await self._updateStatus()
            #print(data)
            await websocket.send(json.dumps(data))
            await asyncio.sleep(self.refresh/2) ## do we need this?

    async def handle(self, message):
        '''deal with incoming messages from the websocket'''
        msg = json.loads(message)
        
        print(msg)
        if 'flap' in msg:
            self._sendFlapRequest(int(msg['flap']))
        if 'arm' in msg:
            self._sendArmRequest(bool(msg['arm']))
        if 'override' in msg:
            # Example: { "override": [1500, 1500, 1500, 1500, 0, 0, 0, 0] }
            self.send_rc_override(msg['override'])
        if 'clear_override' in msg:
            self.clear_rc_override()
        if 'mode' in msg:
            # Example: { "mode": "MANUAL" }
            mode = FlightMode[msg['mode'].upper()]
            self.set_mode(mode)

    

            
        

        
        
