from pymavlink import mavutil
import time
import asyncio
import json
from enum import Enum
from .Logger import Logger

class FlightMode(Enum):
    MANUAL = 0
    STABILISE = 2

class RCWifiControl(Enum):
    RC = 0
    WiFi = 1

class SERVO(Enum):
    FLAP = 2
    ELEVATOR = 1
    AILERON_LEFT = 3
    AILERON_RIGHT = 4
    RUDDER = 5


refresh_time = 0.05
async def asyncRecvMatch(connection, type: str, blocking: bool=False):
    ## blocking isn't necessary
    
    while True:
        m = connection.recv_msg()
        if m is None:
            continue        
        await asyncio.sleep(refresh_time) ## poll through messages
        ## probably easier if there's just one massive message handler
        
        if type == m.get_type():
            print(m)
            return m.to_dict()

class CubeConnection:

    ## might be an idea to move all of the commands to a separate file, as it's making this class extremely long 
    def __init__(self, connection_string, testing=False):
        '''
        Required info from the mav
        '''

        self.req_data = ["ATTITUDE"]

        self.testing = testing
        self.refresh_attitude = 1/10
        self.refresh_servo = 1/2
        self.refresh_heartbeat = 1/1
        self.TIMEOUT = 10
        self._latest_message_ID = 0       
        self.connection_string = connection_string
        self.connection = None
        self.flap_pins = [10]
        self.initialised = asyncio.Event()
        self.refresh_check = 3
        self.blocking = True
        # set up a connection here to the cubepilot
        self.logger = Logger()
        
        self.possible_modes = []
        
            
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
            
                
                self.flap_pins = [10]

                # write params changing servo min and max
                #self.connection.mav.

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

    async def updateStatus(self): 
        '''Function to continually update data and return the data'''
        
        if not self.testing:
            data = await asyncRecvMatch(self.connection, type="ATTITUDE", blocking=True)  # get attitude info
        
        return {
            "time_boot_ms":data["time_boot_ms"],
            "roll":data["roll"],
            "pitch":data["pitch"],
            "yaw":data["yaw"]
        }
    
    def zero_sensor(self):
        pass

    def set_mode(self, mode):
        """
        Set the flight mode of the Cube.
        :param mode: FlightMode Enum (e.g., FlightMode.MANUAL or FlightMode.STABILISE)
        """
        try: # investigate - https://mavlink.io/en/messages/common.html#MAV_CMD_DO_SET_MODE 
            print("hereasdfasdf")
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_SET_MODE, ##### here -> change mode
                0, 
                mode, 0, 0, 0, 0, 0, 0
            )
            
            self.connection.mav.set_mode_send(self.connection.target_system, 0, mode)

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
        if self.testing:
            data = self._testingGenerateData()

    def sendArmRequest(self, arm):
        print("sending request")
        
        print("arm request", arm)
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            int(arm), 21196, 0, 0, 0, 0, 0)
    
    def sendFlapRequest(self, angle): ##todo
        print("requested angle:", angle)
        servo_max_pos = 100
        pwm_command = 2000 - (angle * 2000 / servo_max_pos)
        
        try:
                
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
                    1,
                    SERVO.FLAP,
                    (pwm_command),
                    0,0,0,0,0
            )            
            print("pwm command")   
                    
        except Exception as e:
            print("error sending flap request message")
            print(e)
            

    def update(self, websocket):
        asyncio.gather(self.messageLoop(websocket=websocket))

    async def messageLoop(self, websocket=None):
        refresh_time = 0.005
        #MESSAGE_TYPES = ["HEARTBEAT", "COMMAND_ACK", "NAMED_VALUE_FLOAT", "SERVO_OUTPUT_RAW", "ATTITUDE"]
        self.connection.mav.set_mode_send(self.connection.target_system, mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY, 0) ## turn off safety

        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_RUN_PREARM_CHECKS,
            0,0,0,0,0,0,0,0
        )
        ## change data rates
        self.changeDataRate(0, self.refresh_heartbeat) 
        self.changeDataRate(36, self.refresh_servo)
        self.changeDataRate(30, self.refresh_attitude)

        ## start mate's script
        self.connection.mav.param_set_send(
            self.connection.target_system,
            self.connection.target_component,
            b'SCR_USER1',
            1,
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        self.connection.mav.param_set_send(
            self.connection.target_system,
            self.connection.target_component,
            b'SCR_USER2',
            1,
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )

        ## disable checking before arming the servos
        self.connection.mav.param_set_send(
            self.connection.target_system,
            self.connection.target_component,
            b'ARMING_CHECK',
            0,
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )

        # self.connection.mav.command_long_send(
        #     self.connection.target_system,
        #     self.connection.target_component,
        #     mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        #     0,1,22196,0,0,0,0,0
        # )
        ## force arming?
        
        ## check to see what modes are available

        while True:
            m = self.connection.recv_msg()
            if m is None:
                continue        

            t = m.get_type()
            data = m.to_dict()
            msg = None
            match t:
                case "HEARTBEAT":
                    msg = {
                        "type":"HEARTBEAT",
                        "mode":data["base_mode"],
                        "connected":True,
                        "armed":self.connection.motors_armed()
                    }
                    print("armed: ", self.connection.motors_armed())
                    print("state: ", data["system_status"]) # https://mavlink.io/en/messages/common.html#MAV_STATE
                    self.logger.log(connected=True, armed=self.connection.motors_armed(), mode=data["base_mode"])
                    

                case "COMMAND_ACK":

                    if data["command"] == 511:
                        print("Message interval")
                    elif data["command"] == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
                        print("ARM DISARM REQUEST")
                    print(data)    
                    
                    if data["result"] != 0:
                        msg = {
                            "type":"ERROR",
                            "message":f'Error failed for message command {data["command"]} with status {data["result"]}'
                        }
                        if data["result"] == 2:
                            print("DENIED")
                        elif data["result"] ==4:
                            print("COMMAND FAILED")

                    self.logger.log(command=data["command"], command_result=data["result"])

                case "NAMED_VALUE_FLOAT":
                    if data["name"] == "Sensor":
                        msg = {
                            "type":"FLAP_SENSOR",
                            "time_boot_ms":data['time_boot_ms'],
                            "flapSensorPosition":data["value"]
                        }
                    
                    self.logger.log(time_boot_ms=data["time_boot_ms"], flapSensorPosition=data["value"])

                case "SERVO_OUTPUT_RAW": ### change here to ACTUATOR_OUTPUT_STATUS?
                    try:
                        rawToAngle = lambda a : (a-1100) * 90/900 # check.  Might be better to use scaled outputs instead
                        msg = {
                            "type":"SERVO_OUTPUT_RAW",
                            "flapRequested":rawToAngle(data[f'servo{SERVO.FLAP}_raw']),
                            "aileronL":rawToAngle(data[f"servo{SERVO.AILERON_LEFT}_raw"]),
                            "aileronR":rawToAngle(data[f"servo{SERVO.AILERON_RIGHT}_raw"]),
                            "rudder":rawToAngle(data[f"servo{SERVO.RUDDER}_raw"]),
                            "elevator":rawToAngle(data[f"servo{SERVO.ELEVATOR}_raw"]) # change servo outputs later when final assembly completed
                        }

                    except:
                        print(data)
                    self.logger.log(aileronL=msg["aileronL"], flapRequested=msg["flapRequested"], aileronR=msg["aileronR"], rudder=msg["rudder"], elevator=msg["elevator"])

                case "ATTITUDE":
                    msg = {
                        "type":"ATTITUDE",
                        "time_boot_ms":data["time_boot_ms"],
                        "roll":data["roll"],
                        "pitch":data["pitch"],
                        "yaw":data["yaw"]
                    }
                    self.logger.log(roll=msg["roll"], pitch=msg["pitch"], yaw=msg["yaw"])
                case "AVAILABLE_MODES":
                    print(data)
                
            if msg is not None and websocket is not None:
                await websocket.send(json.dumps(msg))   

            await asyncio.sleep(refresh_time)


    async def handle(self, message):
        '''
        deal with incoming messages from the websocket
        should simplify later -> could be done better with a match/case 
        Should have the FE send a request like
        {
        "type":"request",
        "request":"flap/arm/override etc.",
        "value":123
        }
        rather than
        {
        "type":"request",
        "flap":5
        }
        '''
        try:
            
            msg = json.loads(message)
            
            print(msg) 
            if 'flap' in msg:
                self._sendFlapRequest(int(msg['flap']))  # angle in degrees?
            elif 'arm' in msg:
                print("arming", bool(msg['arm']))
                self.sendArmRequest(bool(msg['arm']))
            elif 'override' in msg:
                # Example: { "override": [1500, 1500, 1500, 1500, 0, 0, 0, 0] }
                print("overriding")
                asyncio.ensure_future(self.send_rc_override(msg['override']))
            elif 'RCWiFiMode' in msg:
                print("changing RC wifi mode")
                nextControlMode = FlightMode(msg['RCWiFiMode'])
                self.clear_rc_override()
            elif 'mode' in msg:
                print("changing mode")
                # Example: { "mode": 81 }
                try:
                    self.set_mode(msg['mode'])
                    self.connection.mav.command_long_send(
                    self.connection.target_system,
                    self.connection.target_component,
                    mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
                    0,
                    435,0, 0, 0, 0, 0, 0)
                except:
                    print("invalid flight mode for message %s", msg)
            
            elif 'sensor' in msg:
                if msg["sensor"] == "zero":
                    ## set sensor 0
                    self.zero_sensor

        except Exception as E:
            print("Error\n"+E)