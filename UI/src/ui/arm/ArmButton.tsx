import {useState} from 'react';
import { Button } from '@mui/material';
import sendArmRequest from '../../connection/request/sendArmRequest';

interface ArmButtonProps {
    armStatus : boolean | undefined
}

export default function ArmButton({armStatus} : ArmButtonProps) {

    const handleArm = () => {
        (armStatus !== undefined) && sendArmRequest(!armStatus) 
    }

    return (
        <div>
            <Button variant="contained" onClick={handleArm} disabled={(armStatus === undefined)}> {armStatus ? "Disarm" : "Arm"}</Button>
        </div>
    )
}