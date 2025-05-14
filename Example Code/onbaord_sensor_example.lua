-- TO DO:
--  - measurement frequency
--  - sensor zeroing

----------------------------------------------
----------------------------------------------
----------------------------------------------

-- PROPERTY OF TEAM 18 OF THE BLUEBIRD CORPORATION, © 2024 BlueBird, ALL RIGHTS RESERVED  --

-- Here I set up the I2C variables: ADDR is the I2C serial address of the sensor itself, REG_ADDR is the registry address of the angle registry 

local ADDR = 0x0F   -- 0x0D, 0x0E or 0x0F depending on hardware configuration
local REG_ADDR = 0x20
local bus = 0   -- = 0 for I2C2 port on the carrier board


-- Here I designate the file path and create a variable that the script will later use as the file

local file_path = "/APM/LOGS/A1335_log_C.csv" -- This way it will be on the SD card, in the logs folder
local file


----------------------------------------------
-- Here I set up the parameters the GCS uses to control the script.

local SCR_U1 = Parameter() -- Will control measurement toggle
local SCR_U2 = Parameter() -- Will control logging toggle
local Zero = Parameter() -- Will control zeroing
local LOG = Parameter() -- Helps log naming
SCR_U1:init('SCR_USER1')
SCR_U2:init('SCR_USER2')
Zero:init('SCR_USER3')
LOG:init('SCR_USER4')
-- The lines above make the updating of the parameters easier. Generally you could just look up the value of the parameter with a single line of code,
-- but that way the cube will search through the whole parameter list fully. This way, by initialising two Parameter type variables, the script saves the 
-- location of the parameter and makes subsequnet lookups really efficient. SCR_U1 and SCR_U2 do not contain the value of the parameter, but the parameter itself.

local U1 = SCR_U1:get()
local U2 = SCR_U2:get()
-- These variables only store the values of the parameters

local is_logging = false    -- These are local variables that help determine if the logging or measuring is toggled on/off
local is_measuring = false

Zero:set_default(0.0)
Zero:set_and_save(0.0)

local log_var = LOG:get()

if type(log_var) ~= number then
    gcs:send_text(6, "LOG param not float, type: " .. tostring(type(log_var)))
    log_var = 2000
end

log_var = log_var + 1
LOG:set_and_save(log_var)

file_path = "/APM/LOGS/sensor_log_port_" .. tostring(log_var) .. ".csv"
----------------------------------------------
----------------------------------------------

local sensor = i2c:get_device(bus, ADDR)    -- Setting up the I2C bus
sensor:set_address(ADDR)    -- Technically you don't need to do this, but it helps make sure the sensor address is the right one

local zero_offset = 0
----------------------------------------------
file = io.open(file_path, "a")  -- Opening the file in write mode and closing it immediately just to erase previous measurements. Might remove this, not sure yet
file:close()
----------------------------------------------


if sensor then  -- Checking I2C setup status, only debug functionality
    gcs:send_text(0, "I2C bus setup complete")
else
    gcs:send_text(0, "I2C bus setup failed")
end

function verify()   -- This function verifies if measuring/logging is turned on/off. is_measuring and is_logging store the current mode of the cube, to help determine if the cube parameters were changed by the GCS (e.g. if is_measuring is 0 and U1 is 1 then measuring has just been turned on)
    U1 = SCR_U1:get()
    U2 = SCR_U2:get()
    --gcs:send_text(1, "is_measuring: " .. tostring(is_measuring))    -- The gcs:send_text() lines in this function serve debug purposes, probably will be removed for final build of the code
    --gcs:send_text(1, "is_logging: " .. tostring(is_logging))
    --gcs:send_text(1, "SCR_ZERO:" .. tostring(Zero:get()))
    if U1 == 1.0 then
        if is_measuring == false then
            gcs:send_text(0, "Beginning sensor measurement")
            is_measuring = true
        end
    else
        if is_measuring == true then
            gcs:send_text(0, "Stopping sensor measurement")
            is_measuring = false
        end
    end
    if U2 == 1.0 then
        if is_logging == false then
            gcs:send_text(0, "Starting logging")
            is_logging = true
        end
    else
        if is_logging == true then
            gcs:send_text(0, "Stopping logging")
            is_logging = false
        end
    end
    if Zero:get() == 1.0 then
        Zero:set_and_save(0.0)
        zero_sensor()
    end
end

function get_clock()    -- Just a function to get the clock
    local time = millis()
    time = tonumber(tostring(time)) -- millis() returns a very weird date type that can't be directly turned into a float, first it needs to be turned into a string (don't ask me why, took me an hour to figure this one line out)
    return time
end


function send_data(data)
    gcs:send_named_float("Sensor", data)    -- This line sends a NAMED_VALUE_FLOAT mavlink message to the GCS. The message has two parts, a string and a float
    --gcs:send_text(6, "Sending angle data to gcs...")    -- Again, debug
end

function read_angle()   -- This function reads the angle registry of the sensor, parses the bits and reads an angle from it
    if is_measuring == true then    -- First, this doesn't need to run if we aren't actually measuring
        local raw_angle = sensor:read_registers(REG_ADDR, 2)    -- sensor is the variable that stores the A1335 as an I2C class; :read_registers() is the standard way you read from the I2C. REG_ADDR is the registry address of the registry that contains the angle data. The second input is the number of bytes we need to read; it is in the documentation (but usually 2)
        if raw_angle then   -- This is a way to catch errors so that they don't crash the script, since it cannot be restarted without a hard reset of the cube
            local high = raw_angle[1]   -- sensor:read_registers() returns a bitarray, meaning the data is split into 8 bit values. Like this: raw_angle: {(first 8 bits), (second 8 bits)}. Keep in mind that some sensors will have the last 8 bits (least significant bits or small bits) first and the first 8 bits (most significant bits or high bits) last (this system is called small endian). Ours is big endian, meaning the first 8 bits (MSB) is read into the first element of the array. (This should be in the documentation, but you can determine it empirically)
            local low = raw_angle[2]    -- The low and high bits are separately extracted from the bitarray
            local angle = (high * 256) + low    -- To recreate the true value of the registry, we must shift the high bits left by 8 places (since they represent larger unit values). Since there is no specific bitwise shift operator in LUA we simply multiply by 2^8 or 256.
            angle = angle & 0x0FFF  -- The first four bits do not contain data about the angle, but rather are used to find the registry, we don't need them. This line is a bitwise AND operation. Result will be 1 if both angle and 0x0FFF(= 0000111111111111) has 1 at the given position. What this does is sets the first four bits to zero, and keeps the rest as they were (since 0x0FFF has 1 at every other place, the final value depends on the bit in angle)
            angle = (angle / 4096) * 360 -- Conversion from bit value to degree, 4096 depends on the system (12bit in our case). You get this by 2^(bit size of the system)
            if (angle - zero_offset) < 0 then
                angle = (360 - math.abs(angle - zero_offset))
            else
                angle = angle - zero_offset
            end
            gcs:send_text(6,"Flap angle: " .. tostring(angle) .. " deg")    -- This way we can see the angle printed in the console
            gcs:send_text(6,"Zero offset: " .. tostring(zero_offset))
            log(angle)  -- Sends angle data to get logged
            send_data(angle)    -- Sends angle data to be transmitted to the GCS
            return angle
        else
            gcs:send_text(6, "Failed read from sensor " .. tostring(ADDR)) -- Mostly debug functionality
        end
    else
        return
    end
end

function open_file()    -- It is better to close the file after each logging operation, so we need a function to open it every time in append mode
    file = io.open(file_path, "a")
    if not file then
        gcs:send_text(6, "File open failed")    -- Once again debug
        return nil
    else
        return
    end
end

function log(angle)
    if is_logging == true then  -- No need to run the function if logging is turned off
        open_file()
        if file then    -- This way we catch an error if the file is not opened correctly.
            local timestamp = get_clock()
            file:write(string.format("%s, %s \n", timestamp, angle))    -- We log the OS clock (time since power on) and the angle data
            file:close()    -- It is better practice to close the file after each write
            return
        else
            gcs:send_text(6, "Logging failed, file open fail") -- Debug
            return
        end
    else
        return
    end
end

function zero_sensor()
    local current = sensor:read_registers(REG_ADDR, 2)
    if current then
        local high = current[1]
        local low = current[2]
        current = (high * 256) + low
        current = current & 0x0FFF
        current = (current / 4096) * 360
        gcs:send_text(6, "Set zero offset to: " .. string.format("%x", ADDR))
        zero_offset = current
    else
        gcs:send_text(6, "Failed current angle read")
    end
end


function update()   -- This is the function that calls everything else, and this is the function that gets called repeatedly by the cube
    -- gcs:send_text(6, "-----------------------------")   -- This way it looks nicer on the console, but will be removed for final software build
    verify()    -- First we verify the control parameters
    read_angle()    -- read_angle will call everything else that it needs
    -- gcs:send_text(6, "-----------------------------")    -- Commented these out as well
    return update, 1000
end


return update() -- The first time the update function is called when the cube is powered up