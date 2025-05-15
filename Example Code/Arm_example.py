from pymavlink import mavutil

def toggle_safety_switch(mav, enable):
    """
    Toggle the safety switch using set_mode_send and MAV_MODE_FLAG_DECODE_POSITION_SAFETY.
    enable=True: safety ON (SAFE)
    enable=False: safety OFF (UNSAFE)
    """
    try:
        mav.mav.set_mode_send(
            mav.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY,
            1 if enable else 0
        )
        print(f"Safety {'Enabled' if enable else 'Disabled'}.")
    except Exception as e:
        print(f"Error toggling safety switch: {e}")

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
    mav = mavutil.mavlink_connection('udp:127.0.0.1:14550')
    mav.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" % (mav.target_system, mav.target_component))

    # Toggle safety switch ON
    toggle_safety_switch(mav, enable=True)

    # Arm the vehicle
    toggle_arming_switch(mav, arm=True)