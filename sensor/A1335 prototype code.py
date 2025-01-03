from machine import Pin, I2C
import time

f = 400000
led = Pin("LED", Pin.OUT, value=0)
ADDRESS = 0x0C
ADDRESS2 = 0x0D
ANGLE_REG = 0x20



class A1335:
    def __init__(self, scl_pin, sda_pin, i2c_id, freq, addr):
        self.i2c = I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)
        print(f"{self} initialised I2C bus.")
        self.ADDR = addr
        self.zero_ang = 0
    
    def get_angle(self):
        data = self.i2c.readfrom_mem(self.ADDR, ANGLE_REG, 2)
        data = ((data[0] << 8) | data[1]) & 0x0FFF
        data = data * (360/4096)
        return data - self.zero_ang
    
    def set_zero(self):
        current_ang = self.get_angle()
        print(f"Setting zero offset to: {current_ang} degrees.")
        self.zero_ang = current_ang
        return
    

sensor1 = A1335(scl_pin=17, sda_pin=16, i2c_id=0, freq=f, addr=ADDRESS)
sensor2 = A1335(scl_pin=17, sda_pin=16, i2c_id=0, freq=f, addr=ADDRESS2)

def angle():
    try:
        led.on()
        print("Begginning measurement")
        time.sleep(0.5)
        while True:
            print(f"Angle: {sensor1.get_angle()} degrees. ")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping.")
    finally:
        led.off()
    return

def angle2():
    try:
        led.on()
        print("Begginning measurement")
        time.sleep(0.5)
        while True:
            print(f"Angle: Sensor 1: {sensor1.get_angle()} degrees, Sensor 2: {sensor2.get_angle()} degrees. ")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping.")
    finally:
        led.off()

