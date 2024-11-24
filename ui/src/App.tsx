import { useState, useEffect, useRef } from 'react';
import TestArtificialHorizon from './ui/artificialHorizon/testArtificialHorizon';
import { FlapControl } from './ui/flightControlSurfaces/flaps/FlapControl';
import AutopilotPanel from './ui/autopilotPanel/AutopilotPanel';
import Grid from "@mui/material/Grid2"
import { connectWebSocket,  getDataRate, latestData, socket } from './connection/connection';
import ArtificialHorizon from './ui/artificialHorizon/ArtificialHorizon';
import ArmButton from './ui/arm/ArmButton';
import {RCModeButton, RCWifiSwitch } from './ui/RC/RCModeButtons';
import RCSendControl from './ui/RC/RCSendControl';

connectWebSocket("ws://localhost:8001")

export default function App () {
    
    const [data, setData] = useState(latestData)
    const [socketState, setSocketState] = useState((socket.readyState === 1))
    const dataRefreshRate=1000/20
    const socketRefreshRate = 1000/500
    useEffect(() => {
        const intervalId1 = setInterval(() => {
            setData({...latestData});
            
        }, dataRefreshRate);

        const intervalId2 = setInterval(() => {
            setSocketState((socket.readyState === 1))
        }, socketRefreshRate)

        return () => {
            clearInterval(intervalId1)
            clearInterval(intervalId2)
        }; 
    }, []);

    //useEffect(()=>console.log(socket.readyState))

    const testing = false;
    const dr = useRef(getDataRate())
    
       
    return (
        <Grid container spacing={1}>
            <div>
                WebSocket status = {socketState ? "connected" : "disconnected"}
                {!socketState && (<div><br /> If UI is disconnected but tms has a connection, please refresh the page</div>)}
            </div>
            <Grid size={12}>
                <AutopilotPanel />
            </Grid>

            <Grid size={6}>

                {testing
                    ? <TestArtificialHorizon />
                    : <ArtificialHorizon roll={data.roll} pitch={data.pitch} />
                }
            </Grid>
            <Grid size={3}> 
                <FlapControl min={0} max={90} posArray={[data.flapSensorPosition, data.flapSensorPosition]}/> {/*THIS LINE FOR FLAP INDICATOR CONFIG 
                    TODO: say whether the cubepilot has received the request
                */}
            </Grid>
            <Grid size={1}>
                <p>
                    Data rate:
                    {dr.current[0]}
                    Data time:
                    {dr.current[1]}
                </p>
                <p>
                   
                </p>
            </Grid>
            <Grid size={2}>
                <RCSendControl />
            </Grid>
            <Grid size={3} >
                <ArmButton armStatus={latestData.armed} />
            </Grid>
            <Grid size={3}>
                <RCModeButton mode={latestData.mode}/>
            </Grid>
            <Grid size={3}>
                {/*<RCWifiSwitch />*/}
            </Grid>

            
        </Grid>
    )
    
}