import { useState, useEffect } from "react";
import TestArtificialHorizon from "./ui/artificialHorizon/testArtificialHorizon";
import { FlapControl } from "./ui/flightControlSurfaces/flaps/FlapControl";
//import AutopilotPanel from "./ui/autopilotPanel/AutopilotPanel";
import Grid from "@mui/material/Grid2"
import { connectWebSocket,  latestData, socket, clearData } from "./connection/connection";
import ArtificialHorizon from "./ui/artificialHorizon/ArtificialHorizon";
import ArmButton from "./ui/arm/ArmButton";
import { RCModeControls /*, RCWifiSwitch*/ } from "./ui/RC/RCModeButtons";
import RCSendControl from "./ui/RC/RCSendControl";
import {LivePlotMemoized} from "./ui/dataHistory/LivePlot"; 
import FlightControlIndicators from "./ui/flightControlSurfaces/indicator/FlightControlIndicators";
import ServoControls from "./ui/flightControlSurfaces/servos/ServoControls";

export default function App() {
    const [data, setData] = useState(latestData);
    const [socketState, setSocketState] = useState(false); // Default to false, to handle unconnected state
    const dataRefreshRate = 1000 / 20; // Update data every 50ms
    const socketRefreshRate = 1000 / 500; // Check socket state every 2ms


    useEffect(() => {
        // Establish WebSocket connection
        connectWebSocket("ws://localhost:8001");

        // Data update interval
        const intervalId1 = setInterval(() => {
            // Ensure latestData is updated correctly
            setData({ ...latestData });
            //console.log(latestData.flapSensorPosition)
        }, dataRefreshRate);

        // Socket connection status interval
        const intervalId2 = setInterval(() => {
            // Check if socket is defined and if it is ready
            setSocketState(socket && socket.readyState === 1);
        }, socketRefreshRate);

        

        return () => {
            clearInterval(intervalId1);
            clearInterval(intervalId2);
        };
    }, [dataRefreshRate, socketRefreshRate]);

    // on first load, clear data arrays (save memory)
    useEffect(() => {
        clearData()
    })

    const testing = false;

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
                {testing ? (
                    <TestArtificialHorizon />
                ) : (
                    <ArtificialHorizon roll={data.roll} pitch={data.pitch} />
                )}
            </Grid>

            {/* RC Mode Controls, indicators */}
            <Grid size={1.75} component="div">
                <RCModeControls mode={latestData.mode} />
                <div style={{ marginTop: "20px" }}>
                <FlightControlIndicators ailL={latestData.servoAileronL} ailR={latestData.servoAileronR} elev={latestData.servoElevator} rud={latestData.servoRudder}/>
                </div>
            </Grid>

            <Grid size={0.25} /> {/*Add some space */}

            {/* Flap Control */}
            <Grid size={2.5} component="div">
                <FlapControl min={0} max={360} requested={data.flapRequestStatus} posArray={[data.flapSensorPosition, data.flapSensorPosition]} />
            </Grid>

            <Grid size={2} component="div">
                <ServoControls />
            </Grid>

            {/* RC Send Control */}
            {/* <Grid size={2} component="div">
                <RCSendControl />
            </Grid> */}
            
            <Grid size={2}>
                Errors:
                {latestData.errorMessages && latestData.errorMessages.map((msg, i) => {
                    return(
                        <div key={i}>
                            {msg}
                        </div>
                    )
                })}
            </Grid>

            {/* Arm Button */}
            <Grid size={3} component="div">
                currently armed? {latestData.armed ? "yes" : "no"}
                <ArmButton armStatus={latestData.armed} />
            </Grid>

            

            {/* LivePlot Component */}
            {/* <Grid size={12}>
                <LivePlotMemoized />
            </Grid> */}
            
        </Grid>
            
        </div>
    );
    
}
