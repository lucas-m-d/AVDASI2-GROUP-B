import { useState } from "react"
import { sendOverrideRCRequest } from '../../connection/request/sendRCRequest';
import { NumberInput } from '../flightControlSurfaces/shared/numberInput';
import { Button } from "@mui/material";

export default function RCSendControl () {
    const [controlValues, setControlValues] = useState<number[]>([0,0,0,0,0,0,0,0]);

    const updateControlValue = (val, i) => {
        var newControlVals = [...controlValues];
        newControlVals[i] = val;
        setControlValues(newControlVals)
    }
    const handleSend = () => {
        sendOverrideRCRequest(controlValues)
    }

    return(
        <div>
            Send custom RC message
            {Array.from({ length: 8 }).map((_, i) => (
                <div key={i}>
                    Param {i + 1}
                    <NumberInput 
                        min={0} 
                        max={3000}
                        value={controlValues[i]}
                        onChange={(_, val) => (updateControlValue(val, i))}
                    />
                </div>
            ))}
            <Button variant="contained" onClick={handleSend}>Send</Button>

        </div>
    )
}