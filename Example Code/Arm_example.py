from pymavlink import mavutil

def toggle_safety_switch(mav, enable):
    """Enable or disable safety switch (using MAV_CMD_DO_SET_MODE)."""
    try:
        # This is a placeholder; actual safety switch control may require a different command
        # Here we just set the mode as an example
        mode = 'STABILIZE'  # or another mode as appropriate
        mode_id = mav.mode_mapping()[mode] if hasattr(mav, 'mode_mapping') else 0
        mav.set_mode(mode_id)
        print(f"Safety {'Enabled' if enable else 'Disabled'} (mode set to {mode}).")
        return True
    except Exception as e:
        print(f"Error toggling safety switch: {e}")
        return False

def toggle_arming_switch(mav, arm):
    """Arm or disarm the vehicle."""
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
    except Exception as e:
        print(f"Error toggling arming switch: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    # Connect to the MAVLink vehicle (UDP endpoint as example)
    mav = mavutil.mavlink_connection('udp:127.0.0.1:14550')
    mav.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" % (mav.target_system, mav.target_component))

    # Toggle safety switch ON
    toggle_safety_switch(mav, enable=True)

    # Arm the vehicle
    toggle_arming_switch(mav, arm=True)