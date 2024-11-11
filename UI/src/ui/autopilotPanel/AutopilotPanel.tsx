import React, {useState, useEffect} from 'react';
import Grid from '@mui/material/Grid2';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import { NumberInput } from '../flightControlSurfaces/shared/numberInput';

export default function AutopilotPanel(){
    const [apHeading, setApHeading] = useState<number | null>(360);
    const [apPitch, setApPitch] = useState<number | null>(0);

    // ensure apheading never goes below 1 or above 360
    useEffect(() => {
        if (apHeading! < 1){
            setApHeading(360 - apHeading!);
        }
        else if (apHeading! > 360){
            setApHeading(apHeading! - 360)
        }
    }, [apHeading])


    const handleApHeadingSend = () => {
        console.log(apHeading)
    }

    const handleApPitchSend = () => {
        console.log(apPitch)
    }

    return (
        <div>
            <Grid container spacing={1}>
                <Grid size={6}>
                    <Stack spacing={2} direction="row">
                    <h2>Heading</h2>
                    <NumberInput
                        min={1} 
                        max={360}
                        value={apHeading}
                        onChange={(_, val) => (setApHeading(val))}
                    />
                    <Button variant="contained" onClick={handleApHeadingSend}>SEND</Button>
                    </Stack>
                </Grid>
                <Grid size={6}>
                    <Stack spacing={2} direction="row">
                    <h2>pitch</h2>
                    <NumberInput
                        min={-45} 
                        max={45}
                        value={apPitch}
                        onChange={(_, val) => (setApPitch(val!))}
                    />
                    <Button variant="contained" onClick={handleApPitchSend}>SEND</Button>
                    </Stack>
                </Grid>
            </Grid>
        </div>

    )

}