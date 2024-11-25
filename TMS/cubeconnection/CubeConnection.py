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

class RCWifiControl(Enum):
    RC = 0
    WiFi = 1



class CubeConnection:

    ## might be an idea to move all of the commands to a separate file, as it's making this class extremely long 
    def __init__(self, connection_string, testing=False):
        '''
        Required info from the mav
        '''

        self.req_data = ["ATTITUDE"]

        self.testing = testing
        self.refresh_attitude = 1/2
        self.refresh_servo = 1/2
        self.refresh_heartbeat = 1/1
        self.TIMEOUT = 10
        self._latest_message_ID = 0       
        self.connection_string = connection_string
        self.connection = None
        self.flap_pins = [10]
        self.initialised = asyncio.Event()
        self.refresh_check = 3
        # set up a connection here to the cubepilot
        
            
        self.time = time.time()

    async def init(self):
        try:
            if not self.testing:
                self.connection = mavutil.mavlink_connection(self.connection_string, baud=111100)
                print("waiting for heartbeat")
                connected = self.connection.wait_heartbeat(timeout=self.TIMEOUT)
                
                if not connected:
                    raise Exception("No connection")
                
                print("Connection: Heartbeat from system (system %u component %u)" % (self.connection.target_system, self.connection.target_component))

                
                
                self._set_mode(129)
                #self._set_mode(128)
                print("here2")
                
                
                
                print(self.connection.motors_armed())
                self.flap_pins = [10]
                self.initialised.set()
            else:
                
                print("testing data")
        except Exception as E:
            print(E)

    def changeDataRate(self, command, rate_s):
        rate_us = rate_s * 1E6
        self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                0,
                command,
                rate_us,
                0,0,0,0,0)
        
        # response = self.connection.recv_match(type="COMMAND_ACK", blocking=True)
        # if response and response.command == command and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        #     print("Command accepted: ", command)
        # else:
        #     print(command)
        #     print("command not accepted")
        #     print(response)
       
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
        
        return {
            "time_boot_ms":data["time_boot_ms"],
            "roll":data["roll"],
            "pitch":data["pitch"],
            "yaw":data["yaw"]
        }
    
    
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
                mode-20,
                mode,
                0, 0, 0, 0, 0, 0
            )
            #print(f"Flight mode set to {mode.name}")

        except Exception as e:
            print("Error setting flight mode:", e)

    async def send_rc_override(self, channels):
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
            #response = self.connection.recv_match(type="COMMAND_ACK", blocking=True)
            #print(response)

            return True
        except Exception as e:
            print("Error sending RC_OVERRIDE:", e)

    def clear_rc_override(self):
        """
        Clear MAVLink RC_OVERRIDE to revert control to the RC transmitter.
        """
        if self.send_rc_override([0, 0, 0, 0, 0, 0, 0, 0]):
            print("RC_OVERRIDE cleared.")


        #     for i in self.req_data:
        #         data.append(self.connection.recv_match(type=i, blocking=True).to_dict()) ## perhaps use a dictionary to get required most recent values from self.connection.messages
        if self.testing:
            data = self._testingGenerateData()
        #print(data)

    
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
                        0,0,0,0,0
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
                0,
            req, 0, 0, 0, 0, 0, 0)

                
        except Exception as e:
            print("error sending arm request message")
            print(e)

    

    async def attitude_loop(self, websocket):
        '''Function to continually update attitude data and return it'''
        self.changeDataRate(30, self.refresh_attitude)

        while True:
            
            if not self.testing:
                data = self.connection.recv_match(type="ATTITUDE", blocking=True).to_dict() # get attitude info
            data = {
            "type":"ATTITUDE",
            "time_boot_ms":data["time_boot_ms"],
            "roll":data["roll"],
            "pitch":data["pitch"],
            "yaw":data["yaw"]
            }
            await websocket.send(json.dumps(data))
            await asyncio.sleep(self.refresh_attitude/self.refresh_check)
    
    async def servo_loop(self, websocket):
        '''Continually update flap request data
        type="SERVO_OUTPUT_RAW"
        '''
        self.changeDataRate(36, self.refresh_servo)
        while True:
            if not self.testing:
                data = self.connection.recv_match(type="SERVO_OUTPUT_RAW", blocking=True).to_dict()
            data = {
                "type":"SERVO_OUTPUT_RAW",
                "flapRequested":data["servo10_raw"]
            }

            await websocket.send(json.dumps(data))
            await asyncio.sleep(self.refresh_servo/self.refresh_check)

    async def flapSensor_loop(self, websocket):
        '''
        ADD FLAP SENSOR FETCHING CODE HERE
        FOR NOW ASSUMING ONLY ONE FLAP SENSOR
        '''
        flapSensorPosition = random.randint(0, 360)
        while True:
            if not self.testing():
                #### get the flap sensor position in this if statement!
                data = self.connection.recv_match(type="NAMED_VALUE_FLOAT", blocking=True).to_dict()
                flapSensorPosition = data["value"]
                #### should work, could you double check if I messed sth up     - Mate
            flapSensorMessage = {
                "type":"FLAP_SENSOR",
                "flapSensorPosition": flapSensorPosition
            }

            await websocket.send(json.dumps(flapSensorMessage))
            await asyncio.sleep((1/2)/self.refresh_check) # get update every half second
             
                

    async def heartbeat_loop(self, websocket):
        self.changeDataRate(0, self.refresh_heartbeat)
        while True:
            if not self.testing:
                data = self.connection.recv_match(type="HEARTBEAT", blocking=True).to_dict()
                
            data = {
                "type":"HEARTBEAT",
                "mode":data["base_mode"],
                "connected":True,
                "armed":self.connection.motors_armed()
                #"armed": self.con.motors_armed()
            }
            print(data)
            await websocket.send(json.dumps(data))
            await asyncio.sleep(self.refresh_heartbeat/self.refresh_check)
    
    async def command_ack_loop(self):
        while True:
            data = self.connection.recv_match(type="COMMAND_ACK", blocking=True).to_dict()
            print(data)
            await asyncio.sleep(0.25)
    

    def update(self, websocket):
        '''take returned data from updateStatus and then send to the websocket'''
        asyncio.gather(
            self.attitude_loop(websocket),
            self.servo_loop(websocket),
            self.heartbeat_loop(websocket),
            self.flapSensor_loop(websocket),
            self.command_ack_loop()
        )   


    async def handle(self, message):
        '''deal with incoming messages from the websocket'''
        try:
            
            msg = json.loads(message)
            
            print(msg)
            if 'flap' in msg:
                self._sendFlapRequest(int(msg['flap']))
            if 'arm' in msg:
                print("arming")
                #self._sendArmRequest(bool(msg['arm']))
            if 'override' in msg:
                # Example: { "override": [1500, 1500, 1500, 1500, 0, 0, 0, 0] }
                print("overriding")
                asyncio.ensure_future(self.send_rc_override(msg['override']))
            if 'RCWiFiMode' in msg:
                print("changing RC wifi mode")
                nextControlMode = FlightMode(msg['RCWiFiMode'])
                self.clear_rc_override()
            if 'mode' in msg:
                print("changing mode")
                # Example: { "mode": "MANUAL" }
                try:
                    mode = FlightMode[msg['mode'].upper()]
                    #self._set_mode(mode)
                except:
                    print("invalid flight mode for message %s", msg)
            #response = self.connection.recv_match(type="COMMAND_ACK", blocking=True)
            #print(response)
        except Exception as E:
            print("Error\n"+E)
            
            

    

            
        

        
        
