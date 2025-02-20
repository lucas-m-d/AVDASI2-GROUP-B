import { Mode } from "@mui/icons-material";

export type DroneData = {
    roll: number | undefined;
    pitch: number | undefined;
    yaw: number | undefined;
    time_boot_ms: number | undefined;
    apMode: number | undefined; // this needs to be redone
    gcsMode: number | undefined; // this needs to be redone
    armed: boolean | undefined;
    flapRequestStatus: number | undefined;
    flapSensorPosition: number | undefined;
    servoAileronL: number | undefined;
    servoAileronR: number | undefined;
    servoRudder: number | undefined;
    servoElevator: number | undefined;
    errorMessages: Array<string | undefined>;
    currentTime: number;
    safety: boolean | undefined;
    text:string[];

};


export let socket: WebSocket;
export let latestData: DroneData = {} as DroneData; // drone data where everything is null


export const clearData = () => {
    latestData = {} as DroneData;
}

const connectWebSocket = (url: string) => {
    
    socket = new WebSocket(url);
    
    socket.onopen = () => {
        console.log("WebSocket connected");
        latestData.text = []
    };

    socket.onmessage = ({ data }: MessageEvent) => {
        const newData = JSON.parse(data);
        const { type } = newData;
        
        latestData.currentTime = Date.now();

        switch (type) {
            case "ATTITUDE": {
                const { time_boot_ms, pitch, roll, yaw } = newData;
                
                Object.assign(latestData, { time_boot_ms, pitch, roll, yaw });
                break;
            }

            case "HEARTBEAT": {
                const { apMode, gcsMode, armed, safety } = newData;
                Object.assign(latestData, { apMode: apMode, gcsMode:gcsMode, armed: !!armed, safety: !!safety });
                break;
            }

            case "SERVO_OUTPUT_RAW": {
                const { flapRequested, aileronL, aileronR, rudder, elevator } = newData;
                console.log(newData)
                Object.assign(latestData, {
                    flapRequestStatus: flapRequested,
                    servoAileronL: aileronL,
                    servoAileronR: aileronR,
                    servoRudder: rudder,
                    servoElevator: elevator,
                });
                break;
            }

            case "ERROR":
                console.error(newData);
                break;

            case "FLAP_SENSOR":
                latestData.flapSensorPosition = newData.flapSensorPosition;
                break;
            
            case "STATUSTEXT":
                latestData.text = [newData.text, ...latestData.text] // place at start
                var textDataLength = latestData.text.length
                if (textDataLength > 50) {
                    latestData.text.splice(49, textDataLength-50)
                }

                break
            default:
                console.warn("Unknown message:", data);
        }
    }

    socket.onclose = () => {
        latestData = {} as DroneData;
        console.log("WebSocket connection closed");
    };
};


const closeWebSocket = () => {
    if (socket) {
        socket.close();
    }
};

export { connectWebSocket, closeWebSocket };