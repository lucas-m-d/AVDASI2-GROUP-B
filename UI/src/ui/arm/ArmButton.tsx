import { Button } from '@mui/material';
import {sendArmRequest, sendSafetyRequest} from '../../connection/request/sendArmRequest';

interface ArmButtonProps {
    armStatus : boolean | undefined
    safety : boolean | undefined
}

export default function ArmButton({armStatus, safety} : ArmButtonProps) {

    const handleArm = () => {
        (armStatus !== undefined) && sendArmRequest(!armStatus) 
    }
    const handleSafety = () => {
        (safety !== undefined) && sendSafetyRequest(!safety)
    }
    

    return (
        <div>
            <Button variant="contained" onClick={handleArm} disabled={(armStatus === undefined)}> {armStatus ? "ARMED" : "DISARMED"}</Button>
            <Button variant="contained" onClick={handleSafety} disabled={(safety === undefined)}> {safety ? "Safety ON" : "Safety OFF"}</Button>
        </div>
    )
}