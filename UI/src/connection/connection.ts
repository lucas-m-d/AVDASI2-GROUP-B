import sendFlapRequest from "./request/sendFlapRequest";
type DroneData = {
    roll: number | null;
    pitch: number | null;
    time_boot_ms: number | null
};
///// lots of this was done in chatgpt

export let socket: WebSocket | null = null;
export let latestData: DroneData | null = null;
export let dataHistory: Array<DroneData> = []
const startTime = Date.now();
var n = 0;

const connectWebSocket = (url: string) => {
    socket = new WebSocket(url);

    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    socket.onmessage = (event: MessageEvent) => {
        console.log("Message received")
        latestData = JSON.parse(event.data); // Store the latest data received
        n = n+1
    };

    socket.onclose = () => {
        latestData = null;
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