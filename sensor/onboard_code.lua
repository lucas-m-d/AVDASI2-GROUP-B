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

local socket = require("socket")

-- Add WebSocket server setup
local server = assert(socket.bind("*", 8080)) -- Bind to port 8080
server:settimeout(0) -- Non-blocking mode
local client -- Holds the WebSocket client connection




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
        gcs:send_text(6, "Flap angle: " .. tostring(angle) .. " deg")
        send_data(angle) -- Send via MAVLink
        send_live_data(angle) -- Send via WebSocket
        log(angle) -- Log to file
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
function check_client()
    if not client then
        client = server:accept() -- Accept new client connection
        if client then
            client:settimeout(0) -- Non-blocking mode for the client
            gcs:send_text(6, "WebSocket client connected")
        end
    end
end

function send_live_data(angle)
    check_client() -- Ensure a client is connected
    if client then
        local timestamp = millis()
        timestamp = tonumber(tostring(timestamp))
        local message = string.format("%s, %s\n", timestamp, angle)
        local success, err = client:send(message)
        if not success then
            gcs:send_text(6, "WebSocket send failed: " .. tostring(err))
            client = nil -- Reset client on failure
        end
    end
end
    


function update()
    check_client() -- Check for WebSocket client connections
    read_raw() -- Read and process sensor data
    return update, 500 -- Call again after 500ms
end



return update()