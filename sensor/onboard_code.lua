-- TO DO:
--  - test angle sensor code while servos connected
--  - test mavlink messaging of angle data
--  - live graphing
--  - measurement frequency

----------------------------------------------
----------------------------------------------
----------------------------------------------

-- PROPERTY OF TEAM 18 OF THE BLUEBIRD CORPORATION, © 2024 BlueBird, ALL RIGHTS RESERVED  --


local ADDR = 0x36
local RAW_ADDR_REG = 0x0C
local bus = 0 --    = 0 for I2C2 port on the carrier board

local file_path = "/APM/LOGS/AS5600_log.csv"
local file

local chan = 0 -- Mavlink channel id

----------------------------------------------

local SCR_U1 = Parameter() -- Will control measurement toggle
local SCR_U2 = Parameter() -- Will control logging toggle
SCR_U1:init('SCR_USER1')
SCR_U2:init('SCR_USER2')
local U1 = SCR_U1:get()
local U2 = SCR_U2:get()
local is_logging = false
local is_measuring = false

----------------------------------------------
----------------------------------------------

local sensor = i2c:get_device(bus, ADDR)
sensor:set_address(ADDR)

----------------------------------------------
file = io.open(file_path, "w")
file:close()
----------------------------------------------


if sensor then
    gcs:send_text(0, "I2C bus setup complete")
else
    gcs:send_text(0, "I2C bus setup failed")
end

function verify()
    U1 = SCR_U1:get()
    U2 = SCR_U2:get()
    gcs:send_text(1, "is_measuring: " .. tostring(is_measuring))
    gcs:send_text(1, "is_logging: " .. tostring(is_logging))
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
end

function get_clock()
    local time = millis()
    time = tonumber(tostring(time))
    return time
end


function send_data(data)
    gcs:send_named_float("Sensor", data)
    gcs:send_text(6, "Sending angle data to gcs...")
end

function read_raw()
    if is_measuring == true then
        local raw_angle = sensor:read_registers(RAW_ADDR_REG, 2)
        if raw_angle then
            local high = raw_angle[1]
            local low = raw_angle[2]
            local angle = (high * 256) + low
            angle = (angle / 4090) * 360
            gcs:send_text(6,"Flap angle: " .. tostring(angle) .. " deg")
            log(angle)
            send_data(angle)
            return
        else
            gcs:send_text(6, "Failed read from sensor")
        end
    else
        return
    end
end

function open_file()
    file = io.open(file_path, "a")
    if not file then
        gcs:send_text(6, "File open failed")
        return nil
    else
        return
    end
end

function log(angle)
    if is_logging == true then
        open_file()
        if file then
            local timestamp = get_clock()
            file:write(string.format("%s, %s \n", timestamp, angle))
            file:close()
            return
        else
            gcs:send_text(6, "Logging failed, file open fail")
            return
        end
    else
        return
    end
end
    


function update()
    gcs:send_text(6, "-----------------------------")   -- This way it looks nicer on the console, but will be removed for final software build
    verify()
    read_raw()
    gcs:send_text(6, "-----------------------------")
    return update, 1000
end


return update()