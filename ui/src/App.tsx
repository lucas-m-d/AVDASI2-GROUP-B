import React, { useState, useEffect, useRef } from 'react';

import TestArtificialHorizon from './ui/artificialHorizon/testArtificialHorizon';
import { FlapControl } from './ui/flightControlSurfaces/flaps/FlapControl';
import AutopilotPanel from './ui/autopilotPanel/AutopilotPanel';
import Grid from "@mui/material/Grid2"
import { connectWebSocket,  getDataRate, latestData } from './connection/connection';
import ArtificialHorizon from './ui/artificialHorizon/ArtificialHorizon';
import ArmButton from './ui/arm/ArmButton';
import {RCModeButton, RCWifiSwitch } from './ui/RC/RCModeButtons';
import RCSendControl from './ui/RC/RCSendControl';

connectWebSocket("ws://localhost:8001")

export default function App () {
    
    const [data, setData] = useState(latestData)

    const refreshRate=1000/20
    
    useEffect(() => {
        const intervalId = setInterval(() => {
            setData({...latestData});
            
        }, refreshRate);

        return () => clearInterval(intervalId); 
    }, []);


    const testing = false;
    const dr = useRef(getDataRate())
    
       
    return (
        <Grid container spacing={1}>
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
                <FlapControl />
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
                <ArmButton />
            </Grid>
            <Grid size={3}>
                <RCModeButton mode={latestData.mode}/>
            </Grid>
            <Grid size={3}>
                <RCWifiSwitch />
            </Grid>

            
        </Grid>
    )
    
}