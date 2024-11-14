import { socket } from '../connection';

interface FlapRequestType {
    type: string,
    arm: boolean
}

export default function sendArmRequest(val: boolean | undefined){
    if (socket) {
        console.log("here")
        const request: FlapRequestType = {
            type: "request",
            arm: val!
        };
        (socket.readyState == socket.OPEN) ? socket.send(JSON.stringify(request)) : console.log("no socket connection")
    }
}