from pymavlink import mavutil

# Connect to the CubePilot through the specified port
connection = mavutil.mavlink_connection('tcp:127.0.0.1:5762')

# Wait for a heartbeat to confirm connection
connection.wait_heartbeat()
print("Heartbeat received from system %u component %u" % (connection.target_system, connection.target_component))

# Disarm the vehicle to ensure safety before manual servo control
print("Disarming the vehicle for safety.")
connection.mav.command_long_send(
    connection.target_system,
    connection.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 0, 0, 0, 0, 0, 0, 0)


# Wait for the disarm command to be acknowledged
msg = connection.recv_match(type='COMMAND_ACK', blocking=True)
if msg.result == 0:
    print("Vehicle disarmed successfully.")
else:
    print("Disarm command failed.")
    exit()  # Exit if disarm fails to ensure safety

# Prompt the user to input values for manual control of elevator (pitch control)
while True:
    try:
        print("\nManual Control of Elevator (Pitch)")
        pwm_value = int(input("Enter the PWM value for the elevator servo (1000-2000, or -1 to quit): "))
        
        if pwm_value == -1:
            print("Exiting manual pitch control.")
            break
        if not 1000 <= pwm_value <= 2000:
            print("Invalid PWM value. Please enter a value between 1000 and 2000.")
            continue

        # Set servo 2 (elevator) to the specified PWM value for pitch control
        connection.mav.command_long_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,     
            2,         
            pwm_value,  # PWM value in microseconds (1000 - 2000)
            0, 0, 0, 0, 0 
        )
        print(f"Command sent to move elevator to {pwm_value} microseconds.")

    except ValueError:
        print("Invalid input.")
    except KeyboardInterrupt:
        print("\nManual control interrupted by user.")
        break

print("Program finished.")
