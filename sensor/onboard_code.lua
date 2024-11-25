-- TO DO:
--  - finish toggling code
--  - test angle sensor code while servos connected
--  - test mavlink messaging of angle data
--  - live graphing

----------------------------------------------
----------------------------------------------
----------------------------------------------


local ADDR = 0x36
local RAW_ADDR_REG = 0x0C
local bus = 0 --    = 0 for I2C2 port on the carrier board

local file_path = "/APM/LOGS/AS5600_log.txt"
local file

local chan = 0 -- Mavlink channel id

-- Measurement/logging toggle (after Gate 2a)
----------------------------------------------

--local SCR_U1 = Parameter() -- Will control measurement toggle
--local SCR_U2 = Parameter() -- Will control logging toggle
--SCR_U1:init('SCR_USER1')
--SCR_U2:init('SCR_USER2')
--local U1 = SCR_U1:get()
--local U2 = SCR_U2:get()
--local is_logging = false
--local is_measuring = false

----------------------------------------------
----------------------------------------------

local sensor = i2c:get_device(bus, ADDR)
sensor:set_address(ADDR)

----------------------------------------------
-- Flushing previous flight data, do we need this?
file = io.open(file_path, "w")
file:close()
----------------------------------------------


if sensor then
    gcs:send_text(0, "I2C bus setup complete")
else
    gcs:send_text(0, "I2C bus setup failed")
end


function send_data(data)
    local message = {
        name = "Sensor reading"     -- Can add specific wing sensor designation later
        value = data
    }
    mavlink:send_message(chan, 251, message)
end

function read_raw()
    local raw_angle = sensor:read_registers(RAW_ADDR_REG, 2)
    if raw_angle then
        local high = raw_angle[1]
        local low = raw_angle[2]
        local angle = (high * 256) + low
        angle = (angle / 4090) * 360
        gcs:send_text(6,"Flap angle: " .. tostring(angle) .. " deg")
        send_data(angle)
        log(angle)
        return
    else
        gcs:send_text(6, "Failed read from sensor")
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
    open_file()
    if file then
        local timestamp = millis()
        timestamp = tonumber(tostring(timestamp))
        file:write(string.format("%s, %s \n", timestamp, angle))
        file:close()
        return
    else
        gcs:send_text(6, "Logging failed, file open fail")
        return
    end
end
    


function update()
    read_raw()
    return update, 500
end


return update()