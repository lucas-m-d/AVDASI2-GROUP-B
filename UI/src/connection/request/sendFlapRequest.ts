import { socket } from '../connection';

interface FlapRequestType {
    type: string,
    flap: number
}

export default function sendFlapRequest(val: number | undefined){
    if (socket && val) {
        const request: FlapRequestType = {
            type: "request",
            flap: val
        };
        socket.send(JSON.stringify(request))
    }
}