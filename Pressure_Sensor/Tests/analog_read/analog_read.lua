--[[----------------------------------------------------------------------------
    analog_read.lua ArduPilot Lua script

    Polls an Arduino (or similar device) on the I2C bus for its analog pin values.

    Intended for use with the I2C_Slave Arduino library.

    CAUTION: This script is capable of engaging and disengaging autonomous control
    of a vehicle.  Use this script AT YOUR OWN RISK.

    Copyright (C) 2024 Yuri Rage

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
------------------------------------------------------------------------------]]

-- Cube and Matek autopilots typically make I2C bus 0 available
-- some Pixhawk (and other) autopilots only expose I2C bus 1
-- set the I2C_BUS variable as appropriate for your board
local I2C_BUS           =    0
local RUN_INTERVAL_MS   =  500
local SLAVE_ADDR        = 0x09
local ERROR_VALUE       = -255
local GET_NUM_PINS      = 0xFE
local SET_PIN_INDEX     = 0xFF
local MAV_SEVERITY_INFO =    6




local num_pins = 0

local arduino_i2c = i2c.get_device(I2C_BUS, SLAVE_ADDR)
arduino_i2c:set_retries(10)


-- see https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Scripting/modules/MAVLink/mavlink_msgs.lua

local message_sender = {}

message_sender.SCRIPTING_PRESSURE_DATA = {}
message_sender.SCRIPTING_PRESSURE_DATA.id = 227
message_sender.SCRIPTING_PRESSURE_DATA.fields = {
    {"pressures", "<I2", 12}
}

message_sender.MEMORY_VECT = {
    id = 249,
    fields = {
        {"address", "<I2"},  -- uint16_t (2 bytes, little-endian)
        {"ver", "<I1"},      -- uint8_t (1 byte, little-endian)
        {"type", "<I1"},     -- uint8_t (1 byte, little-endian)
        {"value", "<i1", 32} -- int8_t[32] (array of 32 signed bytes)
    }
}

-- below: imported from the github.

---Encode the payload section of a given message
---@param msg table -- name of message to encode
---@param message table -- table containing key value pairs representing the data fields in the message
---@return integer -- message id
---@return string -- encoded payload
function message_sender.encode(msg, message)
  gcs:send_text(MAV_SEVERITY_INFO, "Encoding message " .. msg)
    local message_map = msg
    if not message_map then
      -- we don't know how to encode this message, bail on it
      error("Unknown MAVLink message " .. msg)
    end
  
    local packString = "<"
    local packedTable = {}
    local packedIndex = 1
    for i,v in ipairs(message_map.fields) do
      if v[3] then
        packString = (packString .. string.rep(string.sub(v[2], 2), v[3]))
        for j = 1, v[3] do
          packedTable[packedIndex] = message[message_map.fields[i][1]][j]
          if packedTable[packedIndex] == nil then
            packedTable[packedIndex] = 0
          end
          packedIndex = packedIndex + 1
        end
      else
        packString = (packString .. string.sub(v[2], 2))
        packedTable[packedIndex] = message[message_map.fields[i][1]]
        packedIndex = packedIndex + 1
      end
    end
    return message_map.id, string.pack(packString, table.unpack(packedTable))
end


---@param data table -- array of 12 pressure datapoints as integer
---@param numpins number  -- array of 12 pressure datapoints as integer
function message_sender.sendCustomData(data, numpins)
    -- check you have all 12 datapoints
    gcs:send_text(MAV_SEVERITY_INFO, "Sending custom data")
    if type(data) ~= "table" or #data ~= numpins then
        error("too many values or not a table")
    end
    -- see https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Scripting/modules/MAVLink/mavlink_msgs.lua
    local customMessage = {
        pressures = data
    }

    local memoryVectMessage = {
      address = 0x69,
      ver = 1,
      type = 0,
      value = {}  -- Allocate an array of 32 integers
    }

    for i = 1, 32 do
        memoryVectMessage.value[i] = data[i] or 0  -- Populate with data or 0 if missing
    end
    mavlink:send_chan(1, message_sender.encode(message_sender.MEMORY_VECT, memoryVectMessage)) -- we'll see if this works
end





local function unpack_int(b)
    if type(b) ~= 'table' or #b == 0 then return ERROR_VALUE end
    local packed_string = string.char(table.unpack(b))
    -- see https://www.lua.org/manual/5.3/manual.html#6.4.2 for string.unpack format options
    local fmt = ('i%d'):format(#b)  -- signed integer of table size
    local val = string.unpack(fmt, packed_string)
    return val
end

local function read_register_data()
    local bytes = {}
    -- arduino i2c_slave library passes data size in register byte 0
    local size = arduino_i2c:read_registers(0)
    if not size then return nil end
    -- retrieve and store register data
    for idx = 1, size do
        bytes[idx] = arduino_i2c:read_registers(idx)
    end
    return bytes
end

local function get_num_pins()
    arduino_i2c:write_register(GET_NUM_PINS, 0)
    return arduino_i2c:read_registers(1)
end

function update()

    local pressure_data = {}
    for idx = 1, num_pins do
        -- request to store analog pin value in I2C registers for given index
        arduino_i2c:write_register(SET_PIN_INDEX, idx)
        -- now read the register data and collect its value as an signed integer
        local data = read_register_data()
        if data ~= nil then
            pressure_data[idx] = data --lua is 1 based 
        else
            gcs:send_text(MAV_SEVERITY_INFO, "Data for sensor " .. idx .. " was nil")
            return update, RUN_INTERVAL_MS
        end

        --gcs:send_named_float('A' .. idx, unpack_int(data))
        gcs:send_text(MAV_SEVERITY_INFO,  "A" .. idx .. ": " .. unpack_int(data))
    end
    
    message_sender.sendCustomData(pressure_data, num_pins) -- edit this line

    return update, RUN_INTERVAL_MS
end

function init()
    num_pins = get_num_pins()
    if num_pins and num_pins > 0 then
        gcs:send_text(MAV_SEVERITY_INFO, string.format('Analog Read: Monitoring %d pin(s)', num_pins))
        return update, RUN_INTERVAL_MS
    end
    return init, RUN_INTERVAL_MS
end

gcs:send_text(MAV_SEVERITY_INFO, 'Analog Read: Script active')

return init, RUN_INTERVAL_MS
