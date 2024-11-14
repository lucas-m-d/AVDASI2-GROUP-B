import {useState} from 'react';
import { Button } from '@mui/material';
import sendArmRequest from '../../connection/request/sendArmRequest';

export default function ArmButton() {

    const [arm, setArm] = useState(false);
    const handleArm = () => {
        setArm(!arm)
        sendArmRequest(!arm) 
    }

    return (
        <div>
            <Button variant="contained" onClick={handleArm}>{arm ? "Disarm" : "Arm"}</Button>
        </div>
    )
}