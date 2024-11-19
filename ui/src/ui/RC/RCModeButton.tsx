import {useState} from 'react';
import { Button } from '@mui/material';
import { sendRCModeRequest } from '../../connection/request/sendRCRequest';

export default function RCModeButton() {
    // todo, make mode change on manual/stabilise on GCS
    const [mode, setMode] = useState<"MANUAL" | "STABILISE">("MANUAL");
    const handleChangeMode = () => {
        setMode((mode == "MANUAL") ? "STABILISE" : "MANUAL")
        sendRCModeRequest(mode)
    }

    return (
        <div>
            CURRENT MODE: {mode}

            <Button variant="contained" onClick={handleChangeMode}>Set mode to {(mode == "MANUAL") ? "STABILISE" : "MANUAL"}</Button>
        </div>
    )
}