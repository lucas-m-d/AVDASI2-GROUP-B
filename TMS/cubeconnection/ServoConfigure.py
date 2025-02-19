from pymavlink import mavutil
from typing import Callable


from enum import Enum

## remember to edit line 30 
class SERVO(Enum):
    '''Configure the ports connected to the cube'''
    # servo outputs
    # comment next to it is the servo function
    AILERON_PORT = 8 # 4?
    FLAP_PORT = 7 #2
    AILERON_SB = 1 # 4?
    FLAP_SB = 2 #2
    ELEV = 5 # 19
    RUDDER = 4 # 21
    ## placeholder flap 
    FLAP = 13 

class FLAP_PORT_POSITIONS(Enum):
    UP = 0
    TO = 5
    LDG = 25

class FLAP_SB_POSITIONS(Enum):
    UP = 0
    TO = 5
    LDG = 25

## {4, 2, 0, 21, 19, 0, 7, 8} for now

'''
Below will be changed.
___Pwm(angle) -> input angle, output pwm
___Angle(pwm) -> input pwm, output angle
'''

## convert requested angle into output PWM
def AileronPortPwm(angle):
    return float (-19 * angle + 1550)
def FlapPortPwm(angle):
    return float(-19.5 * angle + 2135)
def AileronSBPwm(angle):
    return float (-21.161 * angle + 1392.9)
def FlapSBPwm(angle):
    return float(1508.3 + 22.5 * angle)

def ElevPwm(angle):
    return float(-10.654 * angle + 1555.4)

def RudderPwm(angle):
    return float(12.167*angle + 1200)

### convert PWM values into deflection angle
def AileronPortAngle(pwm):
    return int((pwm - 1500) / -19)
def FlapPortAngle(pwm):
    return int((pwm - 2135) / -19.5)
def AileronSBAngle(pwm):
    return int((pwm - 1392.9) / -21.161)
def FlapSBAngle(pwm):
    return int ((pwm-1508)/22.5)
def ElevAngle(pwm):
    return int((pwm - 1555.4) / -10.654)
def RudderAngle(pwm):
    return int((pwm - 1200) / 12.167)


def mavlink_bytes(string: str):
    return bytes(string, 'UTF-8')

class CubeOrangeServo():
    def __init__(self, pin: int, min:int, max: int, angleToPwm: Callable, pwmToAngle: Callable,  trim: None | int = None, reversed: bool = False):
        self.pin = pin
        self.min = min
        self.max = max
        self.trim = trim
        
        self.angleToPwm = angleToPwm
        self.pwmToAngle = pwmToAngle

        ## if no function defined, the function will return 0
        if self.angleToPwm(15) == None:
            self.angleToPwm = lambda _ : 0 
        if self.pwmToAngle(1500) == None:
            self.pwmToAngle = lambda _ : 0

        self.currentOutAngle = None

        self.reversed = reversed

    def setCurrentOutAngle(self, pwm):
        self.currentOutAngle = self.pwmToAngle(pwm)


class ServoConfiguration():

    def __init__(self, mavlink_connection: mavutil.mavudp | mavutil.mavserial):
        self.con = mavlink_connection
        self.servos_written = False
        
        self.servos: dict[str, type[CubeOrangeServo]] = { ## will need to double/triple check these!
            "AILERON_PORT": CubeOrangeServo(SERVO.AILERON_PORT.value, 950, 2150, AileronPortPwm, AileronPortAngle, trim=1550, reversed=True),
            "FLAP_PORT": CubeOrangeServo(SERVO.FLAP_PORT.value, 1500, 2150, FlapPortPwm, FlapPortAngle, trim=2150, reversed=True),
            "AILERON_SB": CubeOrangeServo(SERVO.AILERON_SB.value, 950, 2150, AileronSBPwm, AileronSBAngle, trim=1400, reversed=True),
            "FLAP_SB": CubeOrangeServo(SERVO.FLAP_SB.value, 1700, 2300, FlapSBPwm, FlapSBAngle, trim=1508),
            "ELEV": CubeOrangeServo(SERVO.ELEV.value, 1050, 2000, ElevPwm, ElevAngle, trim=1550, reversed=True),
            "RUDDER": CubeOrangeServo(SERVO.RUDDER.value, 650, 1600, RudderPwm, RudderAngle, trim=1200, reversed=True)
        }

    
    def writeServoParams(self):
        ### write the servo configuration here
        print("Writing servo parameters.. ")
        for servo in self.servos.values():
            ## type checking
            if type(servo.pin) != int:
                print(f'Servo pin {servo.pin} was not an integer')
                
                return
            
            if servo.pin == SERVO.FLAP.value:continue ## FLAP is a placeholder
            

            self.con.mav.param_set_send(
                self.con.target_system,
                self.con.target_component,
                mavlink_bytes(f'SERVO{servo.pin}_MAX'),
                servo.max,
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            )
            self.con.mav.param_set_send(
                self.con.target_system,
                self.con.target_component,
                mavlink_bytes(f'SERVO{servo.pin}_MIN'),
                servo.min,
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            )

            self.con.mav.param_set_send(
                self.con.target_system,
                self.con.target_component,
                mavlink_bytes(f'SERVO{servo.pin}_REVERSED'),
                int(servo.reversed),
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            )

            if servo.trim is not None:
                self.con.mav.param_set_send(
                    self.con.target_system,
                    self.con.target_component,
                    mavlink_bytes(f'SERVO{servo.pin}_TRIM'),
                    servo.trim,
                    mavutil.mavlink.MAV_PARAM_TYPE_REAL32
                )
            

        print("servo parameters written")

    
    def sendAngle(self, servoReq, angle_degrees):
        '''
        Request an angle to servo(s)
        '''

        print(f"{servoReq}, requested angle:", angle_degrees)

        servosToMove = []
        ## array of [[servo pin, pwm],[servo pin, pwm]]
        
        if servoReq == SERVO.FLAP: ## handle multiple servo messages - if want to move flap (as 2 servos control 1 flap request message)
            try:
                servosToMove.append([self.servos["FLAP_PORT"].pin, self.servos["FLAP_PORT"].angleToPwm(angle_degrees)]) # move the servos
                servosToMove.append([self.servos["FLAP_SB"].pin, self.servos["FLAP_SB"].angleToPwm(angle_degrees)]) # move the servos
            except Exception as E:print(E)

        else:
            try:
                ## find the required servo to move
                servo = None
                for _, i in self.servos.items(): ## for CubeOrangeServo in items()
                    if i.pin==servoReq.value: 
                        servo=i
                        break
                ## check the servo was found
                if servo is not None:
                    servosToMove = [[servo.pin, servo.angleToPwm(angle_degrees)]] ### move servo

                else:raise(IndexError) # if servo was not found raise an error
            except Exception as E:
                print(f'Error finding servo {servoReq}')
                
        ## move servos
        print(servosToMove)
        for servoMovement in servosToMove:
            self.con.mav.command_long_send(
                self.con.target_system,
                    self.con.target_component,
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
                    0,
                    int(servoMovement[0]),
                    float(servoMovement[1]),
                    0,0,0,0,0
            )
    
    def moveFlap(self, RC_Channel_Pwm):
        PWM_HI = 2000
        PWM_LO = 1000
        if RC_Channel_Pwm > PWM_HI:
            # if HI, send UP
            self.sendAngle(SERVO.FLAP_PORT, FLAP_PORT_POSITIONS.UP.value)
            self.sendAngle(SERVO.FLAP_SB, FLAP_SB_POSITIONS.UP.value)
        elif RC_Channel_Pwm < PWM_LO:
            # if LO, send DOWN
            self.sendAngle(SERVO.FLAP_PORT, FLAP_PORT_POSITIONS.LDG.value)
            self.sendAngle(SERVO.FLAP_SB, FLAP_SB_POSITIONS.LDG.value)
        else:
            self.sendAngle(SERVO.FLAP_PORT, FLAP_PORT_POSITIONS.TO.value)
            self.sendAngle(SERVO.FLAP_SB, FLAP_SB_POSITIONS.TO.value)

        
    # def sendAngle(self, servoReq, angle): ##todo
    #     print(f"{servoReq}, requested angle:", angle)
    #     servosToMove = []
    #     pwm_command = 0
    #     try:
    #         match servoReq:
    #             case SERVO.FLAP:
    #                 print("flap request")
    #                 servosToMove = [SERVO.FLAP_PORT.value, SERVO.FLAP_SB.value]
    #                 pwm_command= 1500 + 50 * (angle/30)
                    
    #             case SERVO.AILERON_PORT:
    #                 pwm_command= 1500 + 50 * (angle/30)
    #                 servosToMove = [SERVO.AILERON_PORT.value]
    #                 pass
    #             case SERVO.AILERON_SB:
    #                 pwm_command= 1500 + 50 * (angle/30)
    #                 servosToMove = [SERVO.AILERON_PORT.value]
    #             case SERVO.ELEV:
    #                 servosToMove = [SERVO.ELEV]
    #                 pwm_command= 1500 + 50 * (angle/30)
    #             case SERVO.RUDDER:
    #                 pwm_command= 1500 + 50 * (angle/30)
    #                 servosToMove = [SERVO.AILERON_PORT.value]
                    
    #             case _:
    #                 print("invalid servo request")
    #                 return 
                
    #         for servo in servosToMove:
    #             self.connection.mav.command_long_send(
    #                 self.connection.target_system,
    #                 self.connection.target_component,
    #                 mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
    #                 0,
    #                 servo,
    #                 pwm_command,
    #                 0,0,0,0,0
    #             )
                
    #     except Exception as e:
    #         print("error sending flap request message")
    #         print(e)



### OLD angle conversion data

# rawToAngle = lambda a : (a-1100) * 90/900 # check.  Might be better to use scaled outputs instead
#                         msg = {
#                             "type":"SERVO_OUTPUT_RAW",
#                             "flapRequested":rawToAngle(data[f"servo{SERVO.FLAP.value}_raw"]),
#                             "aileronL":rawToAngle(data[f"servo{SERVO.AILERON_PORT.value}_raw"]),
#                             "aileronR":rawToAngle(data[f"servo{SERVO.AILERON_SB.value}_raw"]),
#                             "rudder":rawToAngle(data[f"servo{SERVO.RUDDER.value}_raw"]),
#                             "elevator":rawToAngle(data[f"servo{SERVO.ELEV.value}_raw"]) # change servo outputs later when final assembly completed
#                         }
