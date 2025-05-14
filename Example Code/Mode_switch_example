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


local servoFunctions = {4, 2, 0, 21, 19, 0, 3, 8}-- servo{n}'s function.  

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
local RC_SCRIPTING = bind_add_param('RC_FUNC', 1, 300)  -- SCcreates a parameter called 'AVDASI2_RC_FUNC' (prefix is from the global definitions section above), in position 1 in the table, and look for changes in the RC input mapped to 'Scripting1' (which is what the '300' means) in Mission Planner
local SAS_SCRIPTING = bind_add_param('SAS_FUNC', 2, 301) --- creates parameter 'SAS_SCRIPTING' at position 1, bound to SCRIPTING_5

-- local variables and definitions
local UPDATE_INTERVAL_MS = 100 -- check for changes 10x/second
local last_rc_switch_pos = -1   -- last known rc switch position.  Used to detect change in RC switch position. Initially set to an impossible value.
local last_sas_switch_pos = -1

-- initialisation
gcs:send_text(MAV_SEVERITY.INFO, "AVDASI2: started") -- just log an info message

-- the main update function
function update() -- we run this whole function every UPDATE_INTERVAL_MS by calling itself again on each 'return'


  -- get RC switch position
  local rc_switch_pos = rc:get_aux_cached(RC_SCRIPTING:get())
  local sas_switch_pos = rc:get_aux_cached(SAS_SCRIPTING:get())

  if not rc_switch_pos then
    -- if rc switch has never been set then return immediately
    return update, UPDATE_INTERVAL_MS -- run the 'update' function again after UPDATE_INTERVAL_MS, don't do anything below here until things are initialised properly
  end

  -- initialise RC switch at startup
  if last_rc_switch_pos == -1 then
    last_rc_switch_pos = rc_switch_pos
  end
  if last_sas_switch_pos == -1 then
    last_sas_switch_pos = sas_switch_pos
  end
  --gcs:send_text(MAV_SEVERITY.INFO, "AVDASI2: test1")
  -- check if user has moved RC switch

  if rc_switch_pos == last_rc_switch_pos and sas_switch_pos == last_sas_switch_pos then -- if nothing has changed...
    
    gcs:send_text(6, string.format("AVDASI2: rc_switch_pos is %d", rc_switch_pos))
    return update, UPDATE_INTERVAL_MS -- ...jump out and end here, setting things up to run again in UPDATE_INTERVAL_MS
  end


  last_rc_switch_pos = rc_switch_pos -- if things have changed then update last position
  last_sas_switch_pos = sas_switch_pos

--####################
--#
--# THIS IS WHERE YOU SET YOUR SERVOS ETC UP
--# Check out the list of servo function settings in Mission Planner/Config/Full parameter list/SERVOn_FUNCTION (n=1,2,3,...)
--# You'll also need to set up your RC and 
--# 
--####################

  -- set servo function based on switch position 
  -- IF ANY SWITCH HAS CHANGED
  if rc_switch_pos == 0 then -- LOW, Manual RC Control
  gcs:send_text(MAV_SEVERITY.INFO, "MANUAL RC CONTROL")
    for servoNumber, servo_function in pairs(servoFunctions) do
      param:set(string.format("SERVO%d_FUNCTION", servoNumber), servo_function)
    end
    -- if MANUAL RC CONTROL, we can change the the mode to STABILISE
    if sas_switch_pos ~= last_sas_switch_pos then
      if sas_switch_pos == 0 then -- LOW, SAS off, MANUAL flight mode
      gcs:send_text(MAV_SEVERITY.INFO, string.format("sas switch pos %d", sas_switch_pos))
        gcs:send_text(MAV_SEVERITY.INFO, "turning to manual mode")
        vehicle:set_mode(0)
      elseif rc_switch_pos == 2 then -- HIGH, 
        gcs:send_text(MAV_SEVERITY.INFO, "turning to stabilise moemode")
        vehicle:set_mode(2)
      end
    end
  end

  if rc_switch_pos == 2 then -- HIGH, TELEM Servo Control
    gcs:send_text(MAV_SEVERITY.INFO, "TELEM Servo Control")
    for servoNumber=1, #servoFunctions do
      --gcs:send_text(6, string.format("SERVO%d_FUNCTION", servoNumber))
      param:set(string.format("SERVO%d_FUNCTION", servoNumber), 0)
    end
    --param:set("SERVO2_FUNCTION",0) -- SERVO2_FUNCTION is set to '0' which tells it that it's disabled, so we can control it from GCS
    --gcs:send_text(6, string.format("AVDASI2: Servo %d function set to %d", 1, 0))
  end


  


  return update, UPDATE_INTERVAL_MS  -- run the 'update' function again after UPDATE_INTERVAL_MS
end

return update()