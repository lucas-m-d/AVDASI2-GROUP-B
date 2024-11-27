import { useState, useEffect, useRef } from "react";
import TestArtificialHorizon from "./ui/artificialHorizon/testArtificialHorizon";
import { FlapControl } from "./ui/flightControlSurfaces/flaps/FlapControl";
import AutopilotPanel from "./ui/autopilotPanel/AutopilotPanel";
import Grid from "@mui/material/Grid";
import { connectWebSocket, getDataRate, latestData, socket } from "./connection/connection";
import ArtificialHorizon from "./ui/artificialHorizon/ArtificialHorizon";
import ArmButton from "./ui/arm/ArmButton";
import { RCModeButton, RCWifiSwitch } from "./ui/RC/RCModeButtons";
import RCSendControl from "./ui/RC/RCSendControl";
import LivePlot from "./ui/dataHistory/liveplot"; 

export default function App() {
    const [data, setData] = useState(latestData);
    const [socketState, setSocketState] = useState(false); // Default to false, to handle unconnected state
    const dataRefreshRate = 1000 / 20; // Update data every 50ms
    const socketRefreshRate = 1000 / 500; // Check socket state every 2ms

    // Ref for data rate
    const dr = useRef(getDataRate());

    useEffect(() => {
        // Establish WebSocket connection
        connectWebSocket("ws://localhost:8001");

        // Data update interval
        const intervalId1 = setInterval(() => {
            // Ensure latestData is updated correctly
            setData({ ...latestData });
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

    const testing = false;

    return (
        <Grid container spacing={1}>
            {/* WebSocket status display */}
            <div>
                WebSocket status = {socketState ? "connected" : "disconnected"}
                {!socketState && (
                    <div>
                        <br /> If UI is disconnected but TMS has a connection, please refresh the page.
                    </div>
                )}
            </div>

            {/* Autopilot Panel */}
            <Grid xs={12} component="div">
                <AutopilotPanel />
            </Grid>

            {/* Artificial Horizon Display */}
            <Grid xs={6} component="div">
                {testing ? (
                    <TestArtificialHorizon />
                ) : (
                    <ArtificialHorizon roll={data.roll} pitch={data.pitch} />
                )}
            </Grid>

            {/* Flap Control */}
            <Grid xs={3} component="div">
                <FlapControl min={0} max={90} posArray={[data.flapSensorPosition, data.flapSensorPosition]} />
            </Grid>

            {/* Data Rate and Time Display */}
            <Grid xs={1} component="div">
                <p>
                    Data rate: {dr.current[0]}<br />
                    Data time: {dr.current[1]}
                </p>
            </Grid>

            {/* RC Send Control */}
            <Grid xs={2} component="div">
                <RCSendControl />
            </Grid>

            {/* Arm Button */}
            <Grid xs={3} component="div">
                <ArmButton armStatus={latestData.armed} />
            </Grid>

            {/* RC Mode Button */}
            <Grid xs={3} component="div">
                <RCModeButton mode={latestData.mode} />
            </Grid>

            {/* LivePlot Component */}
            <Grid xs={12} component="div">
                <LivePlot />
            </Grid>
        </Grid>
    );
}
