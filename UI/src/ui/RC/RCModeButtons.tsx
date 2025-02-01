import {useState} from 'react';
import { Button, MenuItem, Select, FormControl, InputLabel } from '@mui/material';
import { sendRCModeRequest } from '../../connection/request/sendRCRequest';
import { modeFlags } from '../../mavlink/modeFlags';
import Grid from '@mui/material/Grid2';


interface RCModeControlsProps {
    mode: number | undefined
}


export function RCModeControls({ mode }: RCModeControlsProps) {
    const modeFlagNames = Object.values(modeFlags).slice(0, 8); // get names of mode flags
    const flightModeNames = Object.values(FlightMode).slice(0, 24); // get flightmode names
    // const handleChangeMode = (e) => {
    //         if (mode !== undefined) { 
    //             const reqModeFlip = parseInt(e.target.value)
    //             const nextMode = (mode! & reqModeFlip) ? // e.target.value is a number
                
    //                 // if button value is in current mode
    //                 mode! & ~reqModeFlip :
    //                 // if button value is NOT in current mode
    //                 mode! | reqModeFlip
    //             console.log(reqModeFlip)
    //             sendRCModeRequest(nextMode);
    //         }
    // };
    const [flightModeDropdown, setFlightModeDropdown] = useState<FlightMode | unknown>(0)

    return (
        <div>

            <FormControl fullWidth>
                <InputLabel>Flight Mode</InputLabel>
                <Select
                    value={flightModeDropdown}
                    onChange={(event) => {sendRCModeRequest(event.target.value as FlightMode);setFlightModeDropdown(event.target.value)}}
                    label="Flight Mode"
                >
                    {flightModeNames.map((mode) => (
                            <MenuItem key={FlightMode[mode]} value={FlightMode[mode]}>
                                {mode}
                            </MenuItem>
                    ))}
                </Select>
            </FormControl>


            <Grid container>
                {modeFlagNames.map((flag) => // generate button for each mode flag
                    ( 
                        <Grid size={12} key={flag}>
                            <Button
                                fullWidth
                                variant="contained"
                                // onClick={handleChangeMode}
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


enum FlightMode {
    MANUAL = 0,
    CIRCLE = 1,
    STABILIZE = 2,
    TRAINING = 3,
    ACRO = 4,
    FBWA = 5,
    FBWB = 6,
    CRUISE = 7,
    AUTOTUNE = 8,
    AUTO = 10,
    RTL = 11,
    LOITER = 12,
    TAKEOFF = 13,
    AVOID_ADSB = 14,
    GUIDED = 15,
    QSTABILIZE = 17,
    QHOVER = 18,
    QLOITER = 19,
    QLAND = 20,
    QRTL = 21,
    QAUTOTUNE = 22,
    QACRO = 23,
    THERMAL = 24,
    LOITER_TO_QLAND = 25
}