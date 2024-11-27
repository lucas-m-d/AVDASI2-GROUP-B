import { useState, useEffect, useRef } from "react";
import TestArtificialHorizon from "./ui/artificialHorizon/testArtificialHorizon";
import { FlapControl } from "./ui/flightControlSurfaces/flaps/FlapControl";
import AutopilotPanel from "./ui/autopilotPanel/AutopilotPanel";
import Grid from "@mui/material/Grid"; // Fixed import here
import { connectWebSocket, getDataRate, latestData, socket } from "./connection/connection";
import ArtificialHorizon from "./ui/artificialHorizon/ArtificialHorizon";
import ArmButton from "./ui/arm/ArmButton";
import { RCModeButton, RCWifiSwitch } from "./ui/RC/RCModeButtons";
import RCSendControl from "./ui/RC/RCSendControl";
import LivePlot from "./ui/dataHistory/liveplot";
import { createRoot } from "react-dom/client";

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Root element not found");

const root = createRoot(rootElement);
root.render(<LivePlot />);

export default function App() {
    const [data, setData] = useState(latestData);
    const [socketState, setSocketState] = useState(socket.readyState === 1);
    const dataRefreshRate = 1000 / 20;
    const socketRefreshRate = 1000 / 500;

    useEffect(() => {
        connectWebSocket("ws://localhost:8001");

        const intervalId1 = setInterval(() => {
            setData({ ...latestData });
        }, dataRefreshRate);

        const intervalId2 = setInterval(() => {
            setSocketState(socket.readyState === 1);
        }, socketRefreshRate);

        return () => {
            clearInterval(intervalId1);
            clearInterval(intervalId2);
        };
    }, [dataRefreshRate, socketRefreshRate]);

    const testing = false;
    const dr = useRef(getDataRate());

    return (
        <Grid container spacing={1}>
            <div>
                WebSocket status = {socketState ? "connected" : "disconnected"}
                {!socketState && (
                    <div>
                        <br /> If UI is disconnected but tms has a connection, please refresh the page
                    </div>
                )}
            </div>
            <Grid xs={12} component="div">
                <AutopilotPanel />
            </Grid>

            <Grid xs={6} component="div">
                {testing ? (
                    <TestArtificialHorizon />
                ) : (
                    <ArtificialHorizon roll={data.roll} pitch={data.pitch} />
                )}
            </Grid>
            <Grid xs={3} component="div">
                <FlapControl min={0} max={90} posArray={[data.flapSensorPosition, data.flapSensorPosition]} />
            </Grid>
            <Grid xs={1} component="div">
                <p>
                    Data rate: {dr.current[0]}
                    Data time: {dr.current[1]}
                </p>
            </Grid>
            <Grid xs={2} component="div">
                <RCSendControl />
            </Grid>
            <Grid xs={3} component="div">
                <ArmButton armStatus={latestData.armed} />
            </Grid>
            <Grid xs={3} component="div">
                <RCModeButton mode={latestData.mode} />
            </Grid>
        </Grid>
    );
}