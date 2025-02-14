FLAP_PORT_POSITIONS = {
    UP = 0,
    TO = 5,
    LDG = 25
}

FLAP_SB_POSITIONS = {
    UP = 0,
    TO = 5,
    LDG = 25
}

SERVO = {
    FLAP_PORT = 7,  -- Servo ports
    FLAP_SB = 2     -- 
}


--#################### comments in luascript start with '--', the '#'s are just for visibility of this header
--#
--# Example script for AVDASI2 UAV build unit
--# Enables switching of specified servo outputs between RC and ground station control
--# Author: Sid Reid
--# Adapted from https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Scripting/applets/winch-control.lua
--# Useful background - FOLLOW THIS TO ENABLE SCRIPTING: https://ardupilot.org/dev/docs/common-lua-scripts.html
--#
--# TODO: looks like this could be done from Mission Planner's Aux Function screen too - check this https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Scripting/applets/winch-control.md 
--# TODO: is this also a good example of how to do things more elegantly? Not sure https://github.com/ArduPilot/ardupilot/blob/ArduPlane-stable/libraries/AP_Scripting/examples/servo_set_get.lua
--# 
--# You need to:
--#   1. Map a switch on your controller to an output channel (see the Taranis manual) - use a channel that isn't mapped to a flight control!
--#   2. Set the 'RCnn_OPTION' (for channel 'nn') in Mission Planner to '300' (which makes it run 'Scripting1' on change)
--#   
--# This script does the following:
--#   Creates a parameter called 'AVDASI2_RC_FUNC' 
--#   Which looks for changes in the RC input mapped to 'Scripting1'
--#   And runs the update() function below repeatedly, but with a delay of UPDATE_INTERVAL_MS so it doesn't time out or overwhelm the controller
--#   update() (as currently coded) changes SERVO2 (which is usually the elevator) from 'elevator' to 'disabled', so the autopilot will ignore it and you can move it manually
--#
--# To actually run this, your flight controller needs to be armed - you may need to disable some of the prearming checks as you're not actually flying
--# Edit ARMING_CHECK parameter, hit 'set bitmask' for the options here.
--# 
--####################

---@diagnostic disable: param-type-mismatch
-- disable an error message - kept this from the example that this was built on, not sure if it's needed.


-- global definitions
local MAV_SEVERITY = {EMERGENCY=0, ALERT=1, CRITICAL=2, ERROR=3, WARNING=4, NOTICE=5, INFO=6, DEBUG=7} -- you can redefine MAVLINK error codes, these are defaults
local PARAM_TABLE_KEY = 54 -- things are stored in tables, you can have up to 200 - make sure they don't clash
local PARAM_TABLE_PREFIX = "AVDASI2_" -- arbitrary prefix, good for readability and sorting

-- bind a parameter to a variable, so you can address them using easy names rather than numbers
function bind_param(name)
   local p = Parameter()
   assert(p:init(name), string.format("AVDASI2: could not find %s parameter", name))
   return p
end

-- add a parameter and bind it to a variable
function bind_add_param(name, idx, default_value)
   assert(param:add_param(PARAM_TABLE_KEY, idx, name, default_value), string.format("AVDASI2: could not add param %s", name))
   return bind_param(PARAM_TABLE_PREFIX .. name)
end


-- set up our table of parameters
assert(param:add_table(PARAM_TABLE_KEY, PARAM_TABLE_PREFIX, 3), "AVDASI2: could not add param table") -- assign 3 rows to table, in case we want to add anything else later

--[[ -- this is all documentation left over from the template function this script is developed from
  // @Param: RC_FUNC
  // @DisplayName: Mode Switch RC Function
  // @Description: RCn_OPTION number to use to control the mode switch
  // @Values: 300:Scripting1, 301:Scripting2, 302:Scripting3, 303:Scripting4, 304:Scripting5, 305:Scripting6, 306:Scripting7, 307:Scripting8
  // @User: Standard
--]]
local FLAP_POS = bind_add_param('FLAP_POS', 1, 302)  -- Create flap position parameter

-- local variables and definitions
local UPDATE_INTERVAL_MS = 100 -- check for changes 10x/second
local last_flap_switch_pos = -1


function update()
    
    local flap_switch_pos = rc:get_aux_cached(FLAP_POS:get())

    -- if switch position not received
    if not flap_switch_pos then return update, UPDATE_INTERVAL_MS end

    -- 
    if last_flap_switch_pos == -1 then last_flap_switch_pos = flap_switch_pos end

    if flap_switch_pos == last_flap_switch_pos then return update, UPDATE_INTERVAL_MS end



end

return update()