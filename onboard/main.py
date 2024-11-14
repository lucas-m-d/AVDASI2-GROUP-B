from pymavlink import mavutil

from pymavlink.dialects.v20 import common

import time

PORT = 'COM8'

con = mavutil.mavlink_connection("com8")



con.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (con.target_system, con.target_component))



attitude = con.recv_match(type='ATTITUDE',blocking=True) ### this is how you get incoming messages from the cubepilot

con.mav.command_long_send(
    con.target_system,
    con.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
    1,
    10,
    3000,
    0,
    0,
    0,
    0,
    0
)





print(attitude)



