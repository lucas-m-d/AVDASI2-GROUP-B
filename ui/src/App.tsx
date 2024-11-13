import React, { useState, useEffect, useRef } from 'react';

import TestArtificialHorizon from './ui/artificialHorizon/testArtificialHorizon';
import { FlapControl } from './ui/flightControlSurfaces/flaps/FlapControl';
import AutopilotPanel from './ui/autopilotPanel/AutopilotPanel';
import Grid from "@mui/material/Grid2"
import { connectWebSocket, closeWebSocket, getLatestData, getDataRate, latestData, } from './connection/connection';
import ArtificialHorizon from './ui/artificialHorizon/ArtificialHorizon';

connectWebSocket("ws://localhost:8001")

export default function App () {
    
    const [data, setData] = useState(getLatestData())

    const refreshRate=1000/20
    
    useEffect(() => {
        const intervalId = setInterval(() => {
            setData(latestData);
            
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
                    : <ArtificialHorizon roll={data?.roll} pitch={data?.pitch} />
                }
            </Grid>
            <Grid size={3}>
                <FlapControl />
            </Grid>
            <Grid size={3}>
                <p>
                    Data rate:
                    {dr.current[0]}
                    Data time:
                    {dr.current[1]}
                </p>
                <p>
                   
                </p>
            </Grid>
        </Grid>
    )
    
}