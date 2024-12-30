import {useState} from 'react';
import { Button } from '@mui/material';
import { sendRCModeRequest } from '../../connection/request/sendRCRequest';
import { modeFlags } from '../../mavlink/modeFlags';
import Grid from '@mui/material/Grid2';


interface RCModeButtonProps {
    mode: number | undefined
}


export function RCModeButton({ mode }: RCModeButtonProps) {
    const modeFlagNames = Object.values(modeFlags).slice(0, 8); // get names of mode flags

    const handleChangeMode = () => {
            //sendRCModeRequest(newMode);
        
    };

    return (
        <div>
            <Grid container>
            {modeFlagNames.map((flag) => (
                <Grid size={6}>
                    <Button
                        variant="contained"
                        onClick={handleChangeMode}
                        disabled={mode === undefined}
                        color={(mode===undefined) ? "inherit" : ((mode & modeFlags[flag]) ? "success" : "error")}
                    >
                        {flag}
                    </Button>
                </Grid>
            ))}
            </Grid>
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