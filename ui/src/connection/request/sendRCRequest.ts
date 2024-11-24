import { socket } from '../connection';

interface OverrideRCRequestType {
    type: string,
    override: number[]
}

export function sendOverrideRCRequest(overrideArr : number[]){
    if (socket) {
        const request: OverrideRCRequestType = {
            type: "request",
            override: overrideArr
        };
        (socket.readyState == socket.OPEN) ? socket.send(JSON.stringify(request)) : console.log("no socket connection")
    }
} 

interface RCModeRequestType {
    type: string,
    mode: "MANUAL" | "STABILISE"
}

export function sendRCModeRequest(mode : "MANUAL" | "STABILISE"){

    if (socket) {
        const request: RCModeRequestType = {
            type: "request",
            mode: mode
        };
        (socket.readyState == socket.OPEN) ? socket.send(JSON.stringify(request)) : console.log("no socket connection")
    }
} 
export enum RCWifiControlTypes {
    RC = "RC",
    WiFi = "WiFi"
}
interface RCWiFiControlType {
     type: string,
     RCWiFiMode: RCWiFiControlType
}

// export function sendRCWifiSwitch(mode : RCWifiControlTypes) {
//     if (socket) {
//         const request: RCWiFiControlType = {
//             type:"request",
//             RCWiFiMode: mode
//         }
//         (socket.readyState == socket.OPEN) ? socket.send(JSON.stringify(request)) : console.log("no socket connection")
//     }
// }

