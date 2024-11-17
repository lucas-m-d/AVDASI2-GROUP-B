local ADDR = 0x36
local RAW_ADDR_REG = 0x0C
local bus = 0 -- = 0 for I2C2 port on the carrier board

local file_path = "/APM/LOGS/AS5600_log.txt"
local file

local sensor = i2c:get_device(bus, ADDR)
sensor:set_address(ADDR)

file = io.open(file_path, "w")
file:close()

if sensor then
    gcs:send_text(0, "I2C bus setup complete")
else
    gcs:send_text(0, "I2C bus setup failed")
end


function read_raw()
    local raw_angle = sensor:read_registers(RAW_ADDR_REG, 2)
    if raw_angle then
        local high = raw_angle[1]
        local low = raw_angle[2]
        local angle = (high * 256) + low
        angle = (angle / 4090) * 360
        gcs:send_text(6,"Flap angle: " .. tostring(angle) .. " deg")
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
    return update, 1000
end


return update()