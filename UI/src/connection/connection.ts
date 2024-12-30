import sendFlapRequest from "./request/sendFlapRequest";
// type DroneData = {
//     roll: number | null;
//     pitch: number | null;
//     time_boot_ms: number | null
// };
///// lots of this was done in chatgpt
// Types: ATTITUDE, SERVO_OUTPUT_RAW, HEARTBEAT
type DroneData = {
    roll: number | undefined;
    pitch: number | undefined;
    yaw: number | undefined;
    time_boot_ms: number | undefined;
    mode: number | undefined; // this needs to be redone
    armed: boolean | undefined;
    flapRequestStatus: number | undefined;
    flapSensorPosition: number | undefined;
    errorMessages: string[]
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
        if (newData.type=="ATTITUDE"){
            latestData.time_boot_ms = newData.time_boot_ms
            latestData.pitch = newData.pitch
            latestData.roll = newData.roll
            latestData.yaw = newData.yaw
        }
        else if (newData.type === "HEARTBEAT"){
            console.log(newData)
            latestData.mode = newData.mode
            latestData.armed = Boolean(newData.armed)
        } else if (newData.type === "SERVO_OUTPUT_RAW") {
            //console.log(newData.flapRequested)
            latestData.flapRequestStatus = newData.flapRequested
        } else if (newData.type === "ERROR"){
            console.log(newData)
            latestData.errorMessages= latestData.errorMessages ? [...latestData.errorMessages, newData.message] : [newData.message]
            
        } else if (newData.type === "FLAP_SENSOR"){
            console.log(newData)
            latestData.flapSensorPosition = newData.flapSensorPosition
        } else {
            console.log(event.data)
        }
        
        n = n+1
    };

    socket.onclose = () => {
        latestData = {} as DroneData;
        console.log("WebSocket connection closed");
    };
};

const getLatestData = (): DroneData | null => {
    return latestData; // This function is stupid and will get rid of
};

export const getDataRate = () => {
    return [n / (Date.now() - startTime), latestData?.time_boot_ms!*1000] 
}

const closeWebSocket = () => {
    if (socket) {
        socket.close();
    }
};

export { connectWebSocket, getLatestData, closeWebSocket };