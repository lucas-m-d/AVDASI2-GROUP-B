export type DroneData = {
    roll: number | undefined;
    pitch: number | undefined;
    yaw: number | undefined;
    time_boot_ms: number | undefined;
    mode: number | undefined; // this needs to be redone
    armed: boolean | undefined;
    flapRequestStatus: number | undefined;
    flapSensorPosition: number | undefined;
    servoAileronL: number | undefined;
    servoAileronR: number | undefined;
    servoRudder: number | undefined;
    servoElevator: number | undefined;
    errorMessages: Array<string | undefined>;
    currentTime: number;
    safety: boolean | undefined

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
                const { mode, armed } = newData;
                var safety = (newData.mode & 128) != 0// if safety is on
                Object.assign(latestData, { mode, armed: !!armed, safety: !!safety });
                break;
            }

            case "SERVO_OUTPUT_RAW": {
                const { flapRequested, aileronL, aileronR, rudder, elevator } = newData;
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