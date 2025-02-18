from pymavlink import mavutil
import time
import asyncio
import json
from enum import Enum
from .Logger import Logger
from .ServoConfigure import ServoConfiguration, SERVO


from .ArduPilotModes import ArduPilotMode
import traceback

SCRIPTING_PRESSURE_DATA = 227
PRESSURE_SENSOR_MSG_ID = 0xef
FLAP_RC_CHANNEL = 7

REFRESH_TIME_WS_CONNECTED = 1/10000 #s
REFRESH_TIME_WS_DISCONNECTED = 1/50 # s
CUBE_DISCONNECTED_INTERVAL = 2

class FlightMode(Enum):
    MANUAL = 0
    STABILISE = 2

class RCWifiControl(Enum):
    RC = 0
    WiFi = 1

class CubeConnection:

    ## might be an idea to move all of the commands to a separate file, as it's making this class extremely long 
    def __init__(self, connection_string):
        '''
        Required info from the mav
        '''

        self.req_data = ["ATTITUDE"]

        self.refresh_attitude = 1/10
        self.refresh_servo = 1/2
        self.refresh_heartbeat = 1/1
        self.TIMEOUT = 5 ### seconds

        self.connection_string = connection_string
        self.connection = None
        
        self.initialised = asyncio.Event()


        # set up a connection here to the cubepilot
        self.logger = Logger()

        self.servoConfiguration: type[ServoConfiguration] | None = None

            
        self.time = time.time()

    async def init(self):
        try:
            
            self.connection = mavutil.mavlink_connection(self.connection_string, baud=111100)
            print("waiting for heartbeat")
            connected = self.connection.wait_heartbeat(timeout=self.TIMEOUT)

            if not connected:
                print("No connection")
                ##await self.init()
                return
            
            print("Connection: Heartbeat from system (system %u component %u)" % (self.connection.target_system, self.connection.target_component))
            


            #### configure it here
            # write params changing servo min and max
            #self.connection.mav.

            self.servoConfiguration = ServoConfiguration(self.connection)
            self.servoConfiguration.writeServoParams()

            #MESSAGE_TYPES = ["HEARTBEAT", "COMMAND_ACK", "NAMED_VALUE_FLOAT", "SERVO_OUTPUT_RAW", "ATTITUDE"]

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

            # start RC switching script
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

            ## arm cubepilot
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,1,22196,0,0,0,0,0
            )
            self.initialised.set()

            self.ardupilotMode = 0
            self.gcsMode = 0
            
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

    async def sendZeroSensorRequest(self):
        self.connection.mav.param_set_send(
            self.connection.target_system,
            self.connection.target_component,
            b'SCR_USER3',
            1,
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        await asyncio.sleep(0.5) ## sleep for half a second and set the param back to 0 just to make sure
        self.connection.mav.param_set_send(
            self.connection.target_system,
            self.connection.target_component,
            b'SENSOR_ZERO',
            1,
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )

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
                1, mode, 0, 0, 0, 0, 0
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
            return True
        except Exception as e:
            print("Error sending RC_OVERRIDE:", e)

    def clear_rc_override(self):
        """
        Clear MAVLink RC_OVERRIDE to revert control to the RC transmitter.
        """
        if self.send_rc_override([0, 0, 0, 0, 0, 0, 0, 0]):
            print("RC_OVERRIDE cleared.")


    def sendArmRequest(self, arm,force=True):       

        forceSend = 0
        if force:
            forceSend=21196
        if int(arm) ==1:
            print("arming")
        else:
            print("disarming")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            int(arm), forceSend, 0, 0, 0, 0, 0)
        
            

    async def update(self, websocket):
        while not self.initialised.is_set():
            print("awaiting connection")
            print("Waiting for connection to initialise")            
            asyncio.sleep(CUBE_DISCONNECTED_INTERVAL)


        asyncio.gather(self.messageLoop(websocket=websocket))


    async def messageLoop(self, websocket=None):


        while True:
            m = self.connection.recv_msg()
            if m is None:
                continue        

            type = m.get_type()
            data = m.to_dict()
            msg = None

            match type:
                case "ATTITUDE":
                    msg = {
                        "type":"ATTITUDE",
                        "time_boot_ms":data["time_boot_ms"],
                        "roll":data["roll"],
                        "pitch":data["pitch"],
                        "yaw":data["yaw"]
                    }
                

                    self.logger.log(message="ATTITUDE", roll=msg["roll"], pitch=msg["pitch"], pitchrate=data["pitchspeed"], rollrate=data["rollspeed"], yawrate=data["yawspeed"])

                case "HEARTBEAT":
                    #if (data["base_mode"]) == 4:continue
                    #print(mavutil.mode_string_v10(m))
                    if data["autopilot"] == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA:
                        ## if ardupilotmega autopilot
                        self.ardupilotMode = data["base_mode"]
                        
                    elif data["autopilot"] == mavutil.mavlink.MAV_AUTOPILOT_INVALID:
                        ## gcs autopilot
                        self.gcsMode = data["base_mode"]
                    
                    if self.ardupilotMode & mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY:
                        print("wtaf")
                        print(self.ardupilotMode, mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY)

                    #print((self.gcsMode & mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY))
                    msg = {
                        "type":"HEARTBEAT",
                        "apMode":self.ardupilotMode,
                        "gcsMode":self.gcsMode,
                        "connected":True,
                        "armed":self.connection.motors_armed(),
                        "safety":(self.ardupilotMode & mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY)
                    }                        
                    self.logger.log(message="HEARTBEAT", connected=True, armed=self.connection.motors_armed(), mode=data["base_mode"])
                    
                case "COMMAND_ACK":

                    if data["command"] == 511:
                        print("Message interval")
                    elif data["command"] == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
                        print("ARM DISARM REQUEST")
                    elif data["command"] == mavutil.mavlink.MAV_CMD_DO_SET_MODE:
                        print("setting mode command")
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

                    self.logger.log(message="COMMAND_ACK", command=data["command"], command_result=data["result"])

                case "NAMED_VALUE_FLOAT":
                    if data["name"] == "Sensor":
                        pos = data["value"]
                        if pos >= 360:pos = pos - 360

                        msg = {
                            "type":"FLAP_SENSOR",
                            "time_boot_ms":data['time_boot_ms'],
                            "flapSensorPosition":pos
                        }
                    
                    self.logger.log(message="NAMED_VALUE_FLOAT", time_boot_ms=data["time_boot_ms"], flapSensorPosition=data["value"])

                case "SERVO_OUTPUT_RAW": ### change here to ACTUATOR_OUTPUT_STATUS?
                    try:
                        msg = {
                            "type":"SERVO_OUTPUT_RAW",
                            "flapRequested":self.servoConfiguration.servos["FLAP_PORT"].pwmToAngle(data[f'servo{SERVO.FLAP_PORT.value}_raw']), ## flap port for now
                            "aileronL":self.servoConfiguration.servos["AILERON_PORT"].pwmToAngle(data[f'servo{SERVO.AILERON_PORT.value}_raw']),
                            "aileronR":self.servoConfiguration.servos["AILERON_SB"].pwmToAngle(data[f'servo{SERVO.AILERON_SB.value}_raw']),
                            "rudder":self.servoConfiguration.servos["RUDDER"].pwmToAngle(data[f'servo{SERVO.RUDDER.value}_raw']),
                            "elevator":self.servoConfiguration.servos["ELEV"].pwmToAngle(data[f'servo{SERVO.ELEV.value}_raw'])
                        }
                        self.logger.log(message="SERVO_OUTPUT_RAW", aileronL=msg["aileronL"], flapRequested=msg["flapRequested"], aileronR=msg["aileronR"], rudder=msg["rudder"], elevator=msg["elevator"])

                    except Exception as E:
                        print("error here")
                        print(E)
                case "ACTUATOR_OUTPUT_STATUS":
                    try:
                        servoOutputs = data["actuator"]
                        active = data["active"]
                        msg = {
                            "type":"SERVO_OUTPUT_RAW",
                            "flapRequested":self.servoConfiguration.servos["FLAP_PORT"].pwmToAngle(servoOutputs[SERVO.FLAP_PORT.value]), ## flap port for now
                            "aileronL":self.servoConfiguration.servos["AILERON_PORT"].pwmToAngle(servoOutputs[SERVO.AILERON_PORT.value]),
                            "aileronR":self.servoConfiguration.servos["AILERON_SB"].pwmToAngle(servoOutputs[SERVO.AILERON_SB.value]),
                            "rudder":self.servoConfiguration.servos["RUDDER"].pwmToAngle(servoOutputs[SERVO.RUDDER.value]),
                            "elevator":self.servoConfiguration.servos["ELEV"].pwmToAngle(servoOutputs[SERVO.ELEV.value])
                        }
                        self.logger.log(message="ACTUATOR_OUTPUT_STATUS", aileronL=msg["aileronL"], flapRequested=msg["flapRequested"], aileronR=msg["aileronR"], rudder=msg["rudder"], elevator=msg["elevator"])


                    except Exception as E:
                        print(E)
                case "RC_CHANNELS_RAW":
                    try:
                        continue
                        flapChannelValue = data[f"chan{FLAP_RC_CHANNEL}_RAW"] / 100
                        self.servoConfiguration.moveFlap(flapChannelValue)
                        
                    except Exception as E:
                        print(E)
                case "AVAILABLE_MODES":print(data)
                case "BAD_DATA":print(data)
                
            if msg is not None and websocket is not None:
                await websocket.send(json.dumps(msg)) 
                await asyncio.sleep(REFRESH_TIME_WS_CONNECTED)

            if websocket is None:
                await asyncio.sleep(REFRESH_TIME_WS_DISCONNECTED)



    async def handle(self, message):
        '''
        deal with incoming messages from the websocket
        '''
        try:
            
            msg = json.loads(message)
            print(msg) 
            
            if 'flap' in msg:
                self.servoConfiguration.sendAngle(SERVO.FLAP, int(msg['flap']))  # angle in degrees?
            elif 'aileronL' in msg:
                self.servoConfiguration.sendAngle(SERVO.AILERON_PORT, int(msg['aileronL']))
            elif 'aileronR' in msg:
                self.servoConfiguration.sendAngle(SERVO.AILERON_SB, int(msg["aileronR"]))
            elif 'rudder' in msg:
                self.servoConfiguration.sendAngle(SERVO.RUDDER, int(msg['rudder']))
            elif 'elevator' in msg:
                self.servoConfiguration.sendAngle(SERVO.ELEV, int(msg["elevator"]))

            if 'arm' in msg:
                self.sendArmRequest(bool(msg['arm']))
            ## deprecated - RC overriding
            if 'override' in msg:
                print("overriding")
                asyncio.ensure_future(self.send_rc_override(msg['override']))

            ### does this work?
            if 'RCWiFiMode' in msg:
                print("changing RC wifi mode")
                nextControlMode = FlightMode(msg['RCWiFiMode'])
                self.clear_rc_override()
            if 'mode' in msg:
                # Example: { "mode": 81 }
                try:
                    print(f"changing mode to {msg['mode']}.")
                    if msg['mode'] not in [mode.value for mode in ArduPilotMode]:
                        print("requested flight mode may not be available")
                    self.connection.mav.command_long_send(
                        self.connection.target_system,
                        self.connection.target_component,
                        mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                        0,
                        1, msg['mode'], 0,0,0,0,0
                    )
                    #self.set_mode(msg['mode'])
                    
                except Exception as E:
                    print(E)
                    print("invalid flight mode for message %s", msg)
            
            if 'sensor' in msg:
                if msg["sensor"] == "zero":
                    await self.sendZeroSensorRequest()

            if 'safety' in msg:
                try:                  
                    print("turning safety to", int(msg['safety']))  
                    self.connection.mav.set_mode_send(self.connection.target_system, mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY, int(msg['safety'])) ## configure safety
                except Exception as E:
                    print(E)
                    print("invalid safety message %s", msg)
                

        except Exception as E:
            print("Error handling message\n", E)
            print(traceback.format_exc())