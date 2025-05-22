##########################################
#Servo control example python script for AVDASI 2 AVIONICS
#Defines which servo you want to move
#converts given angle to PWM output servo needs that translates to that angle
#Sets maximum and mimimum pwms as well as the trim (0 angle pwm)
#writes the new servo parameters
#sends the wanted angle to the cube
#Author: Ethan Sheehan & Lucas Dick

#This file should be able to run independently
#Potential upgrades:
    #Allow multiple servo movement simultaneously
    #Calibrate to your own servos and mechanisms
    #Checks/confirmation that servos did indeed move

##########################################

from pymavlink import mavutil #make sure pymavlink module is installed


PIN = 8 #defines which servo you want to move

#angle to pwm converter function
def angle_to_pwm(angle):
    return -19 * angle + 1550 #equation found by experimentation with mechanism

#string to bytes converter function
def mav_bytes(string):
    return bytes(string, 'utf-8') #Converts a string to bytes in UTF-8 format, required for MAVLink param names

#Servo class for storing configuration and converting angles to PWM
class Servo:
    def __init__(self, pin, min_pwm=950, max_pwm=2150, trim=1550, reversed=False): #define PWM range and trim
        #Initialize servo configuration with pin and PWM range
        self.pin = pin
        self.min = min_pwm
        self.max = max_pwm
        self.trim = trim
        self.reversed = reversed

    def angle_to_pwm(self, angle): #call function and converts a given angle to its corresponding PWM signal
        return angle_to_pwm(angle)

#ServoController class to configure servo parameters and send angle commands via MAVLink
class ServoController:
    def __init__(self, mav):
        self.mav = mav #MAVLink connection instance
        self.servo = Servo(pin=PIN) #Initialize Servo with predefined pin

    #Write servo parameters function
    def write_servo_params(self):
        print("Setting servo params...")
        for key, val in { #call values defined above
            "MAX": self.servo.max,
            "MIN": self.servo.min,
            "TRIM": self.servo.trim,
            "REVERSED": int(self.servo.reversed)
        }.items():
            self.mav.mav.param_set_send(
                self.mav.target_system,
                self.mav.target_component,
                mav_bytes(f"SERVO{self.servo.pin}_{key}"), #Parameter name in byte format
                val,
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32 #Parameter type
            )
        print("Done.")

    #Send angle command to the servo function
    def send_angle(self, angle):
        pwm = self.servo.angle_to_pwm(angle) #Convert angle to PWM
        print(f"Angle {angle}° → PWM {pwm}")
        self.mav.mav.command_long_send(
            self.mav.target_system,
            self.mav.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #Command to set servo position
            0, self.servo.pin, pwm, 0, 0, 0, 0, 0
        )

#Independence call
if __name__ == "__main__":#allows this script to be ran independently
    #can be used to test if it works before integrating into wider system
    #useful for debugging

    #connect to cute and await heartbeat
    mav = mavutil.mavlink_connection('udp:0.0.0.0:14550')  
    mav.wait_heartbeat()
    print("Heartbeat received from system (system %u component %u)" % (mav.target_system, mav.target_component))

    controller = ServoController(mav)
    controller.write_servo_params()

    #Example: Move servo to 30 degrees
    controller.send_angle(30)
