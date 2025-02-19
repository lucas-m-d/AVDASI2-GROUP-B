import {useState} from 'react'
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import { NumberInput } from '../shared/numberInput';
import { Typography } from '@mui/material';
import { Servo } from '../shared/servo';
import sendServoRequest from '../../../connection/request/sendServoRequest';

export default function ServoControls(){
    const [commandedElevator, setCommandedElevator] = useState<number | undefined>(0)
    const [commandedRudder, setCommandedRudder] = useState<number | undefined>(0)
    const [commandedAileronLeft, setCommandedAileronLeft] = useState<number | undefined>(0)
    const [commandedAileronRight, setCommandedAileronRight] = useState<number | undefined>(0)

    const handleSendCustomElevator = () => {
        sendServoRequest(Servo.Elevator, commandedElevator as number)
    }

    const handleSendCustomRudder = () => {
        sendServoRequest(Servo.Rudder, commandedRudder as number)
    }

    const handleSendCustomAilLeft = () => {
        sendServoRequest(Servo.AilL, commandedAileronLeft as number)
    }

    const handleSendCustomAilRight = () => {
        sendServoRequest(Servo.AilR, commandedAileronRight as number)
    }   

    return (
        <div>
            <Typography variant="h6" align="center">
                Manual servo control
            </Typography>
            <Typography variant="subtitle1">
                Tailplane
            </Typography>
            <Stack
                    direction="column"
                    spacing={4}
                    sx={{
                        justifyContent: "center",
                        alignItems: "center",
                    }}
            >
                {/* Elevator */}
                <Stack spacing={2} direction="row">
                            <NumberInput 
                            min={-30} 
                            max={30}
                            value={commandedElevator}
                            onChange={(_, val) => (setCommandedElevator(Number(val)))}
                            />
                            <Button variant="contained" onClick={handleSendCustomElevator}>ELEV</Button>
                </Stack>
                {/* Rudder */}
                <Stack spacing={2} direction="row">
                            <NumberInput 
                            min={-40} 
                            max={40}
                            value={commandedRudder}
                            onChange={(_, val) => (setCommandedRudder(Number(val)))}
                            />
                            <Button variant="contained" onClick={handleSendCustomRudder}>RUD</Button>
                </Stack>
            </Stack>
            <Typography variant="subtitle1">
                Ailerons
            </Typography>
            <Stack
                    direction="column"
                    spacing={4}
                    sx={{
                        justifyContent: "center",
                        alignItems: "center",
                    }}
            >
                {/* Ail Left */}
                <Stack spacing={2} direction="row">
                            <NumberInput 
                            min={-30} 
                            max={30}
                            value={commandedAileronLeft}
                            onChange={(_, val) => (setCommandedAileronLeft(Number(val)))}
                            />
                            <Button variant="contained" onClick={handleSendCustomAilLeft}>AIL L</Button>
                </Stack>
                {/* Ail Right */}
                <Stack spacing={2} direction="row">
                    <NumberInput 
                        min={-30} 
                        max={30}
                        value={commandedAileronRight}
                        onChange={(_, val) => (setCommandedAileronRight(Number(val)))}
                    />
                    <Button variant="contained" onClick={handleSendCustomAilRight}>AIL R</Button>
                </Stack>                
            </Stack>
            <div>
                    To edit min and max values: go to ui/flightControlSurfaces/servos/ServoControls.tsx
            </div>
        </div>
    )
}