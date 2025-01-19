import {useState} from 'react';
import { Button } from '@mui/material';
import { sendRCModeRequest } from '../../connection/request/sendRCRequest';
import { modeFlags } from '../../mavlink/modeFlags';
import Grid from '@mui/material/Grid2';


interface RCModeControlsProps {
    mode: number | undefined
}


export function RCModeControls({ mode }: RCModeControlsProps) {
    const modeFlagNames = Object.values(modeFlags).slice(0, 8); // get names of mode flags

    const handleChangeMode = (e) => {
            if (mode !== undefined) { 
                const reqModeFlip = parseInt(e.target.value)
                const nextMode = (mode! & reqModeFlip) ? // e.target.value is a number
                
                    // if button value is in current mode
                    mode! & ~reqModeFlip :
                    // if button value is NOT in current mode
                    mode! | reqModeFlip
                console.log(reqModeFlip)
                sendRCModeRequest(nextMode);
            }
    };

    return (
        <div>
            <Grid container>
                {modeFlagNames.map((flag) => // generate button for each mode flag
                    ( 
                        <Grid size={12} key={flag}>
                            <Button
                                fullWidth
                                variant="contained"
                                onClick={handleChangeMode}
                                disabled={mode === undefined}
                                value={modeFlags[flag]}
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