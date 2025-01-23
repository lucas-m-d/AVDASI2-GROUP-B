import { socket } from "../connection";
import { Servo } from "../../ui/flightControlSurfaces/shared/servo"

export default function sendServoRequest(control: number, value: number){
    var messageString: string;
    switch (control) {
        case Servo.AilL: {
            messageString="aileronL"
            break;
        } 
        case Servo.AilR: {
            messageString="aileronR"
            break;
        } case Servo.Elevator: {
            messageString="elevator"
            break;
        } case Servo.Rudder: {
            messageString="rudder"
            break;
        }
        default: {
            console.log("invalid servo request - sendServoRequest.ts")
            return;
        }
    }
    if (socket) {
        const request = JSON.stringify({
            type: "request",
            [messageString]: value
          });

        console.log(request);
        (socket.readyState === socket.OPEN) ? socket.send(request) : console.log("no socket connection")
    }
} 