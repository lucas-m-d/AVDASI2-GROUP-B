##########################################
#Ground Station example python script for AVDASI 2 AVIONICS
#Connects to cube
#Finds heartbeat
#Listens for wanted cube messages
#flags heartbeat disconnection
#Author: Ethan Sheehan

#This file should be able to run independently
#Potential upgrades:
    #Choose which messages you want to listen for
    #Speed up/opptimize process
    #integrate messages into UI

##########################################

from pymavlink import mavutil #make sure pymavlink module is installed
import time

#global variable to store connection status
global connection_status
connection_status = "disconnected"

#Cube connection function
def connect_to_cube():
    print("Connecting to CubePilot...")
    mav = mavutil.mavlink_connection('udp:0.0.0.0:14550') #connects via wifi, should always be the same udp:0.0.0.0:14550
    return mav

#Heartbeat function
def wait_heartbeat(mav):
    print("Waiting for heartbeat...")
    mav.wait_heartbeat() #searches for heartbeat from cube
    print(f"Heartbeat received from system {mav.target_system}, component {mav.target_component}")
    global connection_status
    connection_status = "connected" #update connection status
    print("Status: connected")

#Message listener function
def listen_messages(mav): 
    global connection_status
    last_msg_time = time.time() #time between last message
    timeout = 2  #seconds to consider connection lost

    while True:
        msg = mav.recv_match(type=['SYS_STATUS'], timeout=1) #can change SYS_STATUS to whatever message you desire
        if msg:
            print(f"Received: {msg.get_type()} - {msg.to_dict()}") #prints message in terminal
            last_msg_time = time.time()
            if connection_status != "connected": #shows connected if message received
                connection_status = "connected"
        else:
            # No message received in this interval
            if time.time() - last_msg_time > timeout:
                if connection_status != "disconnected": #shows disconnected if no message received
                    print("Connection lost. Status: disconnected")
                    print("Heartbeat lost!")
                connection_status = "disconnected"
        time.sleep(5) #waits 5 seconds before calling message again

#independence call
if __name__ == "__main__": #allows this script to be ran independently
    #can be used to test if it works before integrating into wider system
    #useful for debugging
    mav = connect_to_cube()
    wait_heartbeat(mav)
    listen_messages(mav)
