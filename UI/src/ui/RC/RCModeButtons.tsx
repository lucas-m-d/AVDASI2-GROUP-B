import {useState} from 'react';
import { Button } from '@mui/material';
import { sendRCModeRequest } from '../../connection/request/sendRCRequest';

interface RCModeButtonProps {
    mode: "MANUAL" | "STABILISE" | undefined
}

export function RCModeButton({ mode }: RCModeButtonProps) {
    const handleChangeMode = () => {
        if (mode !== undefined) {
            const newMode = mode === "MANUAL" ? "STABILISE" : "MANUAL";
            sendRCModeRequest(newMode);
        }
    };

    return (
        <div>
            <p>CURRENT AP MODE: {mode || "UNKNOWN"}</p>
            <Button
                variant="contained"
                onClick={handleChangeMode}
                disabled={mode === undefined}
            >
                {`Set mode to ${mode === "MANUAL" ? "STABILISE" : "MANUAL"}`}
            </Button>
        </div>
    );
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