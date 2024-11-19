import {useState} from 'react';
import { Button } from '@mui/material';
import { sendRCModeRequest } from '../../connection/request/sendRCRequest';

export function RCModeButton() {
    // todo, make mode change on manual/stabilise on GCS
    const [mode, setMode] = useState<"MANUAL" | "STABILISE">("MANUAL");
    const handleChangeMode = () => {
        setMode((mode === "MANUAL") ? "STABILISE" : "MANUAL")
        sendRCModeRequest(mode)
    }

    return (
        <div>
            CURRENT AP MODE: {mode}

            <Button variant="contained" onClick={handleChangeMode}>Set mode to {(mode === "MANUAL") ? "STABILISE" : "MANUAL"}</Button>
        </div>
    )
}

export function RCWifiSwitch() {
    const [mode, setMode] = useState<"WIFI" | "RC">("RC");
    const handleChangeMode = () => {
        setMode((mode === "RC") ? "WIFI" : "RC")
        
    }
    return (
        <div>
            WIFI or RC: {mode}
            <Button variant="contained" onClick={handleChangeMode}>Set mode to {(mode === "RC") ? "WIFI" : "RC"}</Button>
        </div>
    )
}