import { useState, useEffect,memo, useRef } from "react";
import { FlapControl } from "./ui/flightControlSurfaces/flaps/FlapControl";
//import AutopilotPanel from "./ui/autopilotPanel/AutopilotPanel";
import Grid from "@mui/material/Grid2"
import { connectWebSocket,  latestData, socket, clearData, DroneData } from "./connection/connection";
import ArtificialHorizon from "./ui/artificialHorizon/ArtificialHorizon";
import ArmButton from "./ui/arm/ArmButton";
import { RCModeControls /*, RCWifiSwitch*/ } from "./ui/RC/RCModeButtons";
//import RCSendControl from "./ui/RC/RCSendControl";
import {LivePlotMemoized} from "./ui/dataHistory/LivePlot"; 
import FlightControlIndicators from "./ui/flightControlSurfaces/indicator/FlightControlIndicators";
import ServoControls from "./ui/flightControlSurfaces/servos/ServoControls";
import TextDisplay from "./ui/textdisplay/TextDisplay";
import { ServoMinMax } from "./servoMinMax"

const ArtificialHorizonMemoised = memo(ArtificialHorizon)
const FlapControlMemoised = memo(FlapControl)

const dataRefreshMS = 1000 / 5; // Refresh page 10 times a second
const socketRefreshMS = 1000 / 2; // Refresh twice a second

export default function App() {

    const [socketState, setSocketState] = useState(false); // Default to false, to handle unconnected state
    const [, forceUpdate] = useState(0)
    useEffect(() => {
        // Establish WebSocket connection to tms
        connectWebSocket("ws://localhost:8001");
        

        // Data update interval
        const intervalId1 = setInterval(() => {
            // Ensure latestData is updated correctly
            // if (socketState.current) { // check that there is actually new data.  Not doing this basically updates the state if idle at datarefreshrate
            //     console.log("setting state:")

            forceUpdate(i=> i+1)
            
        }, dataRefreshMS);

        // Socket connection status interval
        const intervalId2 = setInterval(() => {
            // Check if socket is defined and if it is ready
            setSocketState(socket.readyState === WebSocket.OPEN) ;
        }, socketRefreshMS);

        

        return () => {
            clearInterval(intervalId1);
            clearInterval(intervalId2);
        };
    }, []);

    // on first load, clear data arrays (save memory)
    useEffect(() => {
        clearData()
    }, []) 

    useEffect(() => {
        console.log("reloading")
    })

    return (
        <div>
            
        <Grid container spacing={1}>
            {/* WebSocket status display */}
            <Grid size={12}>
                <div>
                    WebSocket status = {socketState ? "connected" : "disconnected"}
                    {!socketState && (
                            <p>If UI is disconnected but TMS has a connection, please refresh the page.</p>
                    )}
                </div>
            </Grid>

            {/* Autopilot Panel
            <Grid size={12} component="div">
                <AutopilotPanel />
            </Grid> */}

            {/* Artificial Horizon Display */}
            <Grid size={3.5} component="div">
                <ArtificialHorizonMemoised roll={latestData.roll} pitch={latestData.pitch} />
                ARMED: {latestData.armed ? "YES" : "NO"}
                <ArmButton armStatus={latestData.armed} safety={latestData.safety} />
            </Grid>

            {/* RC Mode Controls, indicators */}
            <Grid size={1.75} component="div">
                <RCModeControls mode={latestData.gcsMode} />
                <div style={{ marginTop: "20px" }}>
                <FlightControlIndicators ailL={latestData.servoAileronL} ailR={latestData.servoAileronR} elev={latestData.servoElevator} rud={latestData.servoRudder}/>
                </div>
            </Grid>

            <Grid size={0.25} /> {/*Add some space */}

            {/* Flap Control */}
            <Grid size={2.5} component="div">
                <FlapControlMemoised min={ServoMinMax.FLAP_SB_MIN} max={ServoMinMax.FLAP_SB_MAX} requested={latestData.flapRequestStatus} posArray={[latestData.flapSensorPosition, latestData.flapSensorPosition]} />
            </Grid>

            <Grid size={3} component="div">
                <ServoControls />
                <TextDisplay textArray={latestData.text}/>
            </Grid>

            {/* RC Send Control */}
            {/* <Grid size={2} component="div">
                <RCSendControl />
            </Grid> */}
            
            {/* <Grid size={2}>
                Errors:
                {latestData.errorMessages && latestData.errorMessages.map((msg, i) => {
                    return(
                        <div key={i}>
                            {msg}
                        </div>
                    )
                })}
            </Grid> */}

            {/* Arm Button */}
            <Grid size={3} component="div">
            </Grid>

            

            {/* LivePlot Component */}
            <Grid size={12}>
                <LivePlotMemoized />
            </Grid>
            
        </Grid>
            
        </div>
    );
    
}
