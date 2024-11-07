import React, { useState, useEffect } from 'react';

import TestArtificialHorizon from './ui/artificialHorizon/testArtificialHorizon';
import { FlapControl } from './ui/flightControlSurfaces/flaps/FlapControl';
import Grid from "@mui/material/Grid2"
import { connectWebSocket, closeWebSocket, getLatestData } from './connection/connection';
import ArtificialHorizon from './ui/artificialHorizon/ArtificialHorizon';
import AttitudeGraph from './ui/dataHistory/AttitudeGraph';

connectWebSocket("ws://localhost:8001")

export default function App () {
    
    const [data, setData] = useState(getLatestData())

    const refreshRate=1/20
    setInterval(() => {
        setData(getLatestData())
    }, refreshRate)
    const testing = false;

    
       
    return (
        <Grid container spacing={1}>
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
                <AttitudeGraph />
            </Grid>
        </Grid>
    )
    
}