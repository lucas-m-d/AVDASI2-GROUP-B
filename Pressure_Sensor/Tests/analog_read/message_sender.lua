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


return message_sender