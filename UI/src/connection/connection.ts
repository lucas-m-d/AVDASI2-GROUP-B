import sendFlapRequest from "./request/sendFlapRequest";
type DroneData = {
    roll: number | null;
    pitch: number | null;
    time_boot_ms: number | null
};
///// lots of this was done in chatgpt

export let socket: WebSocket | null = null;
let latestData: DroneData | null = null;
export let dataHistory: Array<DroneData> = []

const connectWebSocket = (url: string) => {
    socket = new WebSocket(url);

    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    socket.onmessage = (event: MessageEvent) => {
        latestData = JSON.parse(event.data); // Store the latest data received
        dataHistory = [...dataHistory, JSON.parse(event.data)]
 
    };

    socket.onclose = () => {
        latestData = null;
        console.log("WebSocket connection closed");
    };
};

const getLatestData = (): DroneData | null => {
    return latestData; // Return the most recent WebSocket data
};

const closeWebSocket = () => {
    if (socket) {
        socket.close();
    }
};

export { connectWebSocket, getLatestData, closeWebSocket };