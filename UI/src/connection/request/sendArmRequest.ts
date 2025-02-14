import { socket } from '../connection';

interface ArmRequestType {
    type: string,
    arm: boolean
}
interface SafetyRequestType {
    type: string,
    safety: boolean
}

export function sendArmRequest(val: boolean | undefined){
    if (socket) {
        console.log("here")
        const request: ArmRequestType = {
            type: "request",
            arm: val!
        };
        (socket.readyState == socket.OPEN) ? socket.send(JSON.stringify(request)) : console.log("no socket connection")
    }
}
export  function sendSafetyRequest(val: boolean | undefined){
    if (socket) {
        console.log("here")
        const request: SafetyRequestType = {
            type: "request",
            safety: val!
        };
        (socket.readyState == socket.OPEN) ? socket.send(JSON.stringify(request)) : console.log("no socket connection")
    }
}