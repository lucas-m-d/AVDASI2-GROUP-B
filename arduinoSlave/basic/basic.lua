-- Cube and Matek autopilots typically make I2C bus 0 available
-- some Pixhawk (and other) autopilots only expose I2C bus 1
-- set the I2C_BUS variable as appropriate for your board
local I2C_BUS           =    0
local RUN_INTERVAL_MS   =  500
local SLAVE_ADDR        = 0x09
local MAV_SEVERITY_INFO =    6

local arduino_i2c = i2c.get_device(I2C_BUS, SLAVE_ADDR)
arduino_i2c:set_retries(10)

local function read_register_data()
    local bytes = {}
    -- arduino i2c_slave library passes data size in register byte 0
    local size = arduino_i2c:read_registers(0)
    if not size then return nil end
    -- retrieve and store register data
    for idx = 1, size do
        bytes[idx - 1] = arduino_i2c:read_registers(idx)
    end
    return bytes
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
