-- Cube and Matek autopilots typically make I2C bus 0 available
-- some Pixhawk (and other) autopilots only expose I2C bus 1
-- set the I2C_BUS variable as appropriate for your board
local I2C_BUS           =    0
local RUN_INTERVAL_MS   =  500
local SLAVE_ADDR        = 0x09
local MAV_SEVERITY_INFO =    6

local arduino_i2c = i2c.get_device(I2C_BUS, SLAVE_ADDR)
arduino_i2c:set_retries(10)

local file_path = "/APM/LOGS/pressure_log.csv" -- This way it will be on the SD card, in the logs folder
local file

if arduino_i2c then  -- Checking I2C setup status, only debug functionality
    gcs:send_text(0, "I2C bus setup complete")
else
    gcs:send_text(0, "I2C bus setup failed")
end

local function read_register_data()
    local pressure = {}
    -- arduino i2c_slave library passes data size in register byte 0
    local size = arduino_i2c:read_registers(0)
    if not size then return nil end
    -- retrieve and store register data
    for idx = 1, size do
        pressure[idx - 1] = arduino_i2c:read_registers(idx)
    end
    log(pressure)  -- Sends angle data to get logged
    send_data(pressure)    -- Sends angle data to be transmitted to the GCS   
    return pressure
end

function update()
    local val = -255
    local b = read_register_data()
    if b then
        val = 0
        for x = 0, #b do
            val = val | b[x] << (x * 8)
        end
        -- Log the raw value for debugging
        gcs:send_text(MAV_SEVERITY_INFO, 'Raw value received: ' .. tostring(val))
    else
        gcs:send_text(MAV_SEVERITY_INFO, 'Failed to read value from Arduino')
    end
    gcs:send_named_float('A0', val)
    return update, RUN_INTERVAL_MS
end

gcs:send_text(MAV_SEVERITY_INFO, 'Basic I2C_Slave: Script active')

return update, RUN_INTERVAL_MS

--Copied from Mate
local SCR_U1 = Parameter() -- Will control measurement toggle
local SCR_U2 = Parameter() -- Will control logging toggle
SCR_U1:init('SCR_USER1')
SCR_U2:init('SCR_USER2')

local U1 = SCR_U1:get()
local U2 = SCR_U2:get()
-- These variables only store the values of the parameters

local is_logging = false    -- These are local variables that help determine if the logging or measuring is toggled on/off
local is_measuring = false

----------------------------------------------
file = io.open(file_path, "w")  -- Opening the file in write mode and closing it immediately just to erase previous measurements. Might remove this, not sure yet
file:close()
----------------------------------------------

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
    gcs:send_named_float("Pressure", data)    -- This line sends a NAMED_VALUE_FLOAT mavlink message to the GCS. The message has two parts, a string and a float
    --gcs:send_text(6, "Sending angle data to gcs...")    -- Again, debug
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

function log(pressure)
    if is_logging == true then  -- No need to run the function if logging is turned off
        open_file()
        if file then    -- This way we catch an error if the file is not opened correctly.
            local timestamp = get_clock()
            file:write(string.format("%s, %s \n", timestamp, pressure))    -- We log the OS clock (time since power on) and the angle data
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