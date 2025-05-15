from pymavlink import mavutil


PIN = 8

def angle_to_pwm(angle):
    return -19 * angle + 1550

def mav_bytes(string):
    return bytes(string, 'utf-8')

class Servo:
    def __init__(self, pin, min_pwm=950, max_pwm=2150, trim=1550, reversed=False):
        self.pin = pin
        self.min = min_pwm
        self.max = max_pwm
        self.trim = trim
        self.reversed = reversed

    def angle_to_pwm(self, angle):
        return angle_to_pwm(angle)

class ServoController:
    def __init__(self, mav):
        self.mav = mav
        self.servo = Servo(pin=PIN)

    def write_servo_params(self):
        """Sets the servo parameters for the connected MAVLink system."""
        print("Setting aileron params...")
        for key, val in {
            "MAX": self.servo.max,
            "MIN": self.servo.min,
            "TRIM": self.servo.trim,
            "REVERSED": int(self.servo.reversed)
        }.items():
            self.mav.mav.param_set_send(
                self.mav.target_system,
                self.mav.target_component,
                mav_bytes(f"SERVO{self.servo.pin}_{key}"),
                val,
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            )
        print("Done.")

    def send_angle(self, angle):
        """Sends the angle command to the servo."""
        pwm = self.servo.angle_to_pwm(angle)
        print(f"Angle {angle}° → PWM {pwm}")
        self.mav.mav.command_long_send(
            self.mav.target_system,
            self.mav.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0, self.servo.pin, pwm, 0, 0, 0, 0, 0
        )

if __name__ == "__main__":
    # Example usage: connect to MAVLink and control the servo
    mav = mavutil.mavlink_connection('udp:127.0.0.1:14550')  # Adjust as needed
    mav.wait_heartbeat()
    print("Heartbeat received from system (system %u component %u)" % (mav.target_system, mav.target_component))

    controller = ServoController(mav)
    controller.write_servo_params()

    # Example: Move servo to 30 degrees
    controller.send_angle(30)
