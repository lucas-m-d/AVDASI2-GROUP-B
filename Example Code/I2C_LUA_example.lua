-- LUA I2C example script for AVDASI 2
-- Reads data from a sensor over I2C, translates it into legible data and sends it to the Ground Control Station using MAVLink
-- Author: Mate Kadas

-- This code is written to work with an A1335LLETR-T Magnetic Hall Effect Sensor
-- You are NOT SUPPOSED TO COPY AND PASTE this, but are encouraged to use it as help in writing your own code
--------------------------------------------------
--------------------------------------------------


-- Declaring variables----------------------------

local ADDR = 0x0C -- I2C address of the sensor
local REG_ADDR = 0x20 -- Registry of the raw angle data

local filepath = "/APM/LOGS/A1335_log.csv" -- The Cube has a logs folder by default, this code will save a custom csv of the results there
--------------------------------------------------
--------------------------------------------------


-- Setting up I2C bus-----------------------------

local sensor = i2c:get_device(0, ADDR)
--------------------------------------------------
--------------------------------------------------

file = io.open(file_path, "a")  -- Opening the file in write mode and closing it immediately just to erase previous measurements. WILL OVERWRITE PREVIOUS FILE
file:close()

if sensor then  -- Checks I2C setup status and sends a status message (can be seen in Mission Planner, or captured as a MAVLink STATUSTEXT message)
    gcs:send_text(0, "I2C bus setup complete") -- The number is the msg severity from 0 to 6 with zero being critical
else
    gcs:send_text(0, "I2C bus setup failed")
end

function get_clock()    -- Just a function to get the clock (lot of core functionality unaccessible in this LUA environment, wacky solutions like this must be used)
    local time = millis()
    time = tonumber(tostring(time)) -- millis() returns a very weird date type that can't be directly turned into a float, first it needs to be turned into a string
    return time
end

function read_angle()   -- This function reads the angle registry of the sensor, parses the bits and reads an angle from it (Big Endian version)
    local raw_angle = sensor:read_registers(REG_ADDR, 2)    -- :read_registers() is the standard way you read from the I2C. The second input is the number of bytes we need to read; it is in the documentation (but usually 2)
    if raw_angle then   -- This is a way to catch errors so that they don't crash the script, since it cannot be restarted without a hard reset of the Cube
        local high = raw_angle[1]   -- sensor:read_registers() returns a bitarray, meaning the data is split into 8 bit values. Like this: raw_angle: {(first 8 bits), (second 8 bits)}. Keep in mind that some sensors will have the last 8 bits (least significant bits or small bits) first and the first 8 bits (most significant bits or high bits) last (this system is called small endian). The A1335 is big endian, meaning the first 8 bits (MSB) is read into the first element of the array. (This should be in the documentation, but can be determined it empirically)
        local low = raw_angle[2]    -- The low and high bits are separately extracted from the bitarray
        local angle = (high * 256) + low    -- To recreate the true value of the registry, we must shift the high bits left by 8 places (since they represent larger unit values). Since there is no specific bitwise shift operator in LUA we simply multiply by 2^8 or 256.
        angle = angle & 0x0FFF  -- (THIS IS SPECIFIC TO THIS SENSOR COMPONENT!!) The first four bits do not contain data about the angle, but rather are used to find the registry, these are not needed. This line is a bitwise AND operation. Result will be 1 if both angle and 0x0FFF(= 0000111111111111) has 1 at the given position. What this does is sets the first four bits to zero, and keeps the rest as they were (since 0x0FFF has 1 at every other place, the final value depends on the bit in angle)
        angle = (angle / 4096) * 360 -- Conversion from bit value to degree, 4096 depends on the system (12bit in our case). You get this by 2^(bit size of the system); Can be found in the documentation of the sensor
        log(angle)  -- Sends angle data to get logged
        send_data(angle)    -- Sends angle data to be transmitted to the GCS
        return angle
    end
end

function read_angle_small()   -- This is the same function as the one above, but the Small Endian version
    local raw_angle = sensor:read_registers(REG_ADDR, 2)    
    if raw_angle then
        local high = raw_angle[2]  -- Just changed the index
        local low = raw_angle[1]
        local angle = (high * 256) + low
        angle = angle & 0x0FFF
        angle = (angle / 4096) * 360
        log(angle)
        send_data(angle)
        return angle
    end
end

function send_data(data)  -- This function sends the angle as a NAMED_VALUE_FLOAT MAVLink message (only this and gcs:send_text can be used by LUA scripts)
    gcs:send_named_float("Sensor", data)    -- The message has two parts, a string (usually a designator) and a float (the data)
end


function log(angle)
    file = io.open(file_path, "a")  -- It is better to open and close the log file every time something is to be logged
    if file then
        local timestamp = get_clock()
        file:write(string.format("%s, %s \n", timestamp, angle))    -- The OS clock (time since power on) and the angle data is logged into separate columns
        file:close()    -- It is good practice to close the file after each write
        return
    else
        return
    end
end

-- LUA scripts on the Cube work by continuously calling an update function with a set delay (this way the script runs as long as the Cube operates)
function update()   -- This is the function that calls everything else, and this is the function that gets called repeatedly by the cube
    read_angle()    -- read_angle will call everything else that it needs
    return update, 1000  -- This is where the delay before recursion is specified
end

return update() -- The first time the update function is called when the cube is powered up