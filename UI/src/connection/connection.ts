import sendFlapRequest from "./request/sendFlapRequest";


type DroneData = {
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
};


export let socket: WebSocket;
export let latestData: DroneData = {} as DroneData; // drone data where everything is null
export let dataHistory: Array<DroneData> = []
const startTime = Date.now();
var n = 0;

const connectWebSocket = (url: string) => {
    socket = new WebSocket(url);
    
    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    socket.onmessage = (event: MessageEvent) => {

        var newData = JSON.parse(event.data);
        switch (newData.type){
            case "ATTITUDE":
                latestData.time_boot_ms = newData.time_boot_ms;
                latestData.pitch = newData.pitch;
                latestData.roll = newData.roll;
                latestData.yaw = newData.yaw;
                break;
    
            case "HEARTBEAT":
                console.log(newData);
                latestData.mode = newData.mode;
                latestData.armed = Boolean(newData.armed);
                break;

            case "SERVO_OUTPUT_RAW":
                latestData.flapRequestStatus = newData.flapRequested;
                latestData.servoAileronL = newData.aileronL;
                latestData.servoAileronR = newData.aileronR;
                latestData.servoRudder = newData.rudder;
                latestData.servoElevator = newData.elevator;
                break;

            case "ERROR":
                console.log(newData);
                //latestData.errorMessages =  [...latestData.errorMessages!, newData.message]

                break;

            case "FLAP_SENSOR":
                console.log(newData);
                latestData.flapSensorPosition = newData.flapSensorPosition;
                break;

            default:
                console.log(event.data);
                break;
        }
        
        
        n += 1
    };

    socket.onclose = () => {
        latestData = {} as DroneData;
        console.log("WebSocket connection closed");
    };
};


export const getDataRate = () => {
    return [n / (Date.now() - startTime), latestData?.time_boot_ms!*1000] 
}

const closeWebSocket = () => {
    if (socket) {
        socket.close();
    }
};

export { connectWebSocket, closeWebSocket };