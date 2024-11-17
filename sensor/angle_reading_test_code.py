from machine import Pin, I2C
import time


ADDR = 0x36

RAW_ANGLE_REG = 0x0C
led = Pin("LED", Pin.OUT)
f = 400000
ANGLE_REG = 0x0E
ZPOS_W = 0x02
ZPOS_R = 0x01
MANG = 0x06


led.off()

class AS5600:
    def __init__(self, scl_pin, sda_pin, i2c_id=0, freq=f):
        self.i2c = I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=f)
        self.address = ADDR

    def read_raw_angle(self):
        data = self.i2c.readfrom_mem(self.address, RAW_ANGLE_REG, 2)
        raw_angle = (data[0] << 8) | data[1]
        return raw_angle & 0x0FFF

    def get_angle_degrees(self):
        raw_angle = self.read_raw_angle()
        angle_degrees = (raw_angle / 4096.0) * 360.0
        return angle_degrees
    
    def read_scaled(self):
        data = self.i2c.readfrom_mem(self.address, ANGLE_REG, 2)
        angle = (data[0] << 8) | data[1]
        angle = angle & 0x0FFF
        angle_degrees = (angle / 4096.0) * 360.0
        return angle_degrees
    
    def calibrate(self, Range):
        current = self.read_raw_angle()
        bit = current.to_bytes(1)
        self.i2c.writeto_mem(self.address, ZPOS_W, bit)
        print(f"Wrote {current} into ZPOS")
        time.sleep(0.1)
        range_b = Range.to_bytes(1)
        self.i2c.writeto_mem(self.address, MANG, range_b)
        print(f"Wrote {Range} into MANG")
        return None
    
    def check_start(self):
        raw = self.i2c.readfrom_mem(self.address, ZPOS_R, 2)
        angle_proper = (raw[0] << 8) | raw[1]
        return (angle_proper / 4096.0) * 360.0
    
    
            
    
def begin_measurement(sensor):
    log = []
    led.on()
    tic = time.ticks_ms()
    try:
        while True:
            angle = sensor.get_angle_degrees()
            print(f"Angle: {angle:.2f} degrees")
            toc = time.ticks_ms()
            log.append([time.ticks_diff(toc, tic), angle])
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Measurement stopped by user.")
    finally:
        led.off()
        write_data(input(">> Please enter savefile name \n"), log)

def burst(sensor):
    for i in range(0, 25):
        angle = sensor.read_scaled()
        angle_raw = sensor.get_angle_degrees()
        print(f"Angle registry gives: {angle};  Raw angle registry gives: {angle_raw}")
        time.sleep(0.5)

def write_data(filename, data):
    with open(f"{filename}.csv", 'w') as f:
        f.write("Time (ms), Angle (deg) \n")
        for x in data:
            f.write(','.join(map(str, x)) + '\n')
    

sensor = AS5600(scl_pin=17, sda_pin=16)


    


