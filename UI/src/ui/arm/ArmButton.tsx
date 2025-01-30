import {useState} from 'react';
import { Button } from '@mui/material';
import sendArmRequest from '../../connection/request/sendArmRequest';

interface ArmButtonProps {
    armStatus : boolean | undefined
}

export default function ArmButton({armStatus} : ArmButtonProps) {

    const [armed, setArmed] = useState(armStatus);
    const handleArm = () => {
        (armStatus !== undefined) && sendArmRequest(!armed) 
    }

    return (
        <div>
            <Button variant="contained" onClick={handleArm} disabled={(armStatus === undefined)}> {armed ? "Arm" : "Disarm"}</Button>
        </div>
    )
}