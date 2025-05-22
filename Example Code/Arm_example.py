##########################################
#Arming example python script for AVDASI 2 AVIONICS
#Arms/Disarms cube (which also allows logging)
#Toggles Safety Switch (locks servo movement)
#Author: Ethan Sheehan

#This file should be able to run independently
#Potential upgrades:
    #You can add more streamline ways to execute these functions 
    #Add your own checks and safeties
    #Automate when disarm/safety on need to happen

##########################################

from pymavlink import mavutil #make sure pymavlink module is installed

#Global variable to store the safety state
safety_state = None

#Safety Switch function
def toggle_safety_switch(mav, enable):

    #Toggle the safety switch using set_mode_send and MAV_MODE_FLAG_DECODE_POSITION_SAFETY.
        #enable=True: safety ON (SAFE)
        #enable=False: safety OFF (UNSAFE)
    
    try:
        mav.mav.set_mode_send(
            mav.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY,
            1 if enable else 0 # 1 = safety on, 0 = safety off
        )
        print(f"Safety {'Enabled' if enable else 'Disabled'}.")
        return True
    except Exception as e: #error handling
        print(f"Error toggling safety switch: {e}")
        return False

#Arming function
def toggle_arming_switch(mav, arm):

    #Arm/Disarm using MAV_CMD_COMPONENT_ARM_DISARM

    try:
        mav.mav.command_long_send(
            mav.target_system,
            mav.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # Confirmation
            1 if arm else 0,  # 1 = arm, 0 = disarm
            0, 0, 0, 0, 0, 0
        )
        print(f"Arming {'Enabled' if arm else 'Disabled'}.")
        return True
    except Exception as e: #error handling
        print(f"Error toggling arming switch: {e}")
        return False

#Independence call
if __name__ == "__main__": #allows this script to be ran independently
    #can be used to test if it works before integrating into wider system
    #useful for debugging

    #connect to cute and await heartbeat
    mav = mavutil.mavlink_connection('udp:0.0.0.0:14550')
    mav.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" % (mav.target_system, mav.target_component))

    # Toggle safety switch ON
    toggle_safety_switch(mav, enable=True)

    # Arm the vehicle
    toggle_arming_switch(mav, arm=True)