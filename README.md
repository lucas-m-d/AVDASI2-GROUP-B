# AVDASI2-GROUP-B
 
UI - handles everything the user sees
TMS - handles all communication with the drone.

Think of the TMS as a middle man. The UI cannot itself communicate to the drone; it needs something in the middle to do that work for it.

The TMS will constantly stream data to the websocket regarding the drone's sttate