import { socket } from '../connection';

export function sendZeroSensorRequest(){

    if (socket) {
        const request = {
            "type": "request",
            "sensor":"zero"
        };
        console.log(JSON.stringify(request));
        (socket.readyState === socket.OPEN) ? socket.send(JSON.stringify(request)) : console.log("no socket connection")
    }
} 