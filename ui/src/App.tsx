import React, { useState, useEffect } from 'react';

import TestArtificialHorizon from './ui/artificialHorizon/testArtificialHorizon';
import { FlapControl } from './ui/flightControlSurfaces/flaps/FlapControl';
import Grid from "@mui/material/Grid2"
import { connectWebSocket, closeWebSocket, getLatestData } from './connection/connection';
import ArtificialHorizon from './ui/artificialHorizon/ArtificialHorizon';


export default function App () {
    

    connectWebSocket("ws://localhost:8001")
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
                
            </Grid>
        </Grid>
    )
    
}