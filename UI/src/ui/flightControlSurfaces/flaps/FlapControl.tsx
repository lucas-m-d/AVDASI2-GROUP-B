import Box from '@mui/material/Box';
import Slider from '@mui/material/Slider';
import { Typography } from '@mui/material';
//import Grid from "@mui/material/Grid2"
import { NumberInput } from '../shared/numberInput';
import { useState, useEffect} from 'react';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import FlapIndicator from './FlapIndicator';
//import testFlapIndicator from './testFlapIndicator';
import sendFlapRequest from '../../../connection/request/sendFlapRequest';
import { sendZeroSensorRequest } from '../../../connection/request/sendZeroSensorRequest';

interface flapPosition {
    value: number,
    label: string,
}

const flapSettings: flapPosition[] = [
    {
        value: 0,
        label: "UP"
    },
    {
        value:10,
        label:"T/O"
    },
    {
        value:25,
        label:"LDG"
    },
    {
        value:30,
        label:"FULL"
    }
]

interface FlapControlProps {
    min : number,
    max : number,
    posArray : [number?, number?],
    requested : number | undefined
}

export function FlapControl({min, max, posArray, requested} : FlapControlProps) {

    const [commandedFlap, setCommandedFlap] = useState<number | undefined>(undefined)
    const [showFlap, setShowFlap] = useState<number>(commandedFlap ? commandedFlap : 0)
    
    const [customFlapInputValue, setCustomFlapInputValue] = useState<number>(0)
    // todo: require enter key and handle bad values
    requested = requested ?? 0
    const handleSliderChange = (event: Event, newValue: number | number[]) => {
        setCommandedFlap(newValue as number);
        setShowFlap(newValue as number)
        setCustomFlapInputValue(newValue as number)
      };

    const handleSendCustomFlap = () => {
        setShowFlap(customFlapInputValue);
        setCommandedFlap(customFlapInputValue)
    }
    

    // handle flap command
    useEffect(() => {
        sendFlapRequest(commandedFlap)
    }, [commandedFlap])

    return (
        <Box sx={{width:300}}>
            
            <Stack
                    direction="column"
                    spacing={4}
                    sx={{
                        justifyContent: "center",
                        alignItems: "center",
                    }}
            >
                <Typography variant="h3" align="center">FLAPS</Typography>
            
                    
                    <Slider 
                        value={showFlap}
                        aria-label="Custom marks"
                        defaultValue={0}
                        marks={flapSettings}
                        step={null}
                        valueLabelDisplay="auto"
                        min={0}
                        max={flapSettings[flapSettings.length-1].value}
                        onChange={handleSliderChange}
                    />
                    
                    <div>
                    <Typography align="center" variant="subtitle1">Custom Flap Position</Typography>
                    <Stack spacing={2} direction="row">
                        <NumberInput 
                        min={0} 
                        max={flapSettings[flapSettings.length-1].value}
                        value={customFlapInputValue}
                        onChange={(_, val) => (setCustomFlapInputValue(Number(val)))}
                        />
                        <Button variant="contained" onClick={handleSendCustomFlap}>SEND</Button>
                    </Stack>
                    </div>
                    <div style={{ justifyContent: "center",}}>
                        <div style={{ display: "flex", justifyContent: "center", marginTop: "20px" }}>
                            <Typography variant="h5" align="center">FLAP GAUGES</Typography>
                        </div>

                        <div style={{ display: "flex", justifyContent: "center", marginTop: "20px" }}>
                            <FlapIndicator min={min} max={max} request={requested} position={posArray} />
                        </div>

                        <div style={{ display: "flex", justifyContent: "center", marginTop: "20px" }}>
                            <Button variant="contained" onClick={sendZeroSensorRequest}>ZERO SENSOR</Button>
                        </div>
                        
                        <br /> Flap position value = {Math.round(posArray[0]!)} {posArray[0] === undefined && (<div style={{display:"inline-block"}}>unknown</div>)}
                        <br /> <br />Set max/min flap positions by going to: <br />"./src/App.tsx" and editing the <br />{"<FlapControl min={0} max={90} />"} line
                    </div>
                    
            </Stack> 
            
        </Box>
    )

}