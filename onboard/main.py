from pymavlink import mavutil

PORT = 'COM8'

con = mavutil.mavlink_connection("tcp:localhost:5760")



con.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (con.target_system, con.target_component))

print("sending time")
con.system_time_send()


attitude = con.recv_match(type='ATTITUDE',blocking=True) ### this is how you get incoming messages from the cubepilot

print(attitude)



