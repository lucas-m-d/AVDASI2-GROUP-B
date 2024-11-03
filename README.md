# AVDASI2-GROUP-B
 
UI - handles everything the user sees
TMS - handles all communication with the drone.

Think of the TMS as a middle man. The UI cannot itself communicate to the drone; it needs something in the middle to do that work for it.

The TMS will constantly stream data to the websocket regarding the drone's state


How do I run this?


1) install node.js
2) install python

3) go into ./ui and, in a command prompt, run
```npm i```
4) install the python dependency mavlink

```pip install mavlink```

5) go into ./ui and run "npm run start"
6) go into ./TMS and run "python main.py"

you may need to refresh the ui to get the websocket connection working

