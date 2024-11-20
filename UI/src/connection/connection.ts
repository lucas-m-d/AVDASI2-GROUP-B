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
    mode: "MANUAL" | "STABILISE" | undefined;
    armed: boolean | undefined;
    flapRequestStatus: boolean | undefined;
};


export let socket: WebSocket | null = null;
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
        else if (newData.type == "HEARTBEAT"){
            latestData.mode = newData.mode
        } else if (newData.type == "SERVO_OUTPUT_RAW") {
            latestData.flapRequestStatus = newData.flapRequested
        } else if (newData.type == "ERROR"){
            console.log(newData)
        } else {
            console.log(event.data)
        }
        //latestData = JSON.parse(event.data); // Store the latest data received
        n = n+1
    };

    socket.onclose = () => {
        latestData = <DroneData>{};
        console.log("WebSocket connection closed");
    };
};

const getLatestData = (): DroneData | null => {
    return latestData; // Return the most recent WebSocket data
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