import { useState, useEffect, memo, useRef } from "react";
import CSS from "csstype";
import { latestData } from "../../connection/connection";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer } from 'recharts';
import { ServoMinMax } from "../../servoMinMax";
import { Servo } from "../flightControlSurfaces/shared/servo";

type LivePlotDataPoint = {
    time: number;
    value: number | undefined;
};

const livePlotStyles = {
    plotWidth: 500,
    plotHeight: 500,
    rowHeight: "450px",
};

const livePlotRowStyle: CSS.Properties = {
    width: "inherit",
    height: livePlotStyles.rowHeight,
    overflowX: "auto",
    overflowY: "hidden",
    whiteSpace: "nowrap",
};

const updateIntervalMS = 1000 / 2;
const maxDisplayTimeS = 120; // 2 minutes
const maxDataLength = (maxDisplayTimeS * 1e3) / updateIntervalMS;

export const LivePlotMemoized = memo(function LivePlot() {
    const loadTime = useRef(Date.now());

    // Separate state for each data point
    const [pitchData, setPitchData] = useState<LivePlotDataPoint[]>([]);
    const [rollData, setRollData] = useState<LivePlotDataPoint[]>([]);
    const [yawData, setYawData] = useState<LivePlotDataPoint[]>([]);
    const [flapData, setFlapData] = useState<LivePlotDataPoint[]>([]);
    const [ailLData, setAilLData] = useState<LivePlotDataPoint[]>([]);
    const [ailRData, setAilRData] = useState<LivePlotDataPoint[]>([]);
    const [elevData, setElevData] = useState<LivePlotDataPoint[]>([]);
    const [rudData, setRudData] = useState<LivePlotDataPoint[]>([]);

    useEffect(() => {
        const intervalId = setInterval(() => {
            if (latestData.time_boot_ms !== undefined) {
                const newTime = Date.now() - loadTime.current;

                const addData = (setData, newValue) => {
                    setData((oldData) => {
                        if (oldData[oldData.length - 1]?.value !== newValue) { // Fixed syntax
                            const newData = [...oldData, { time: newTime, value: newValue }];
                            return newData.length > maxDataLength ? newData.slice(1) : newData;
                        }
                        return oldData; 
                    });
                };

                addData(setPitchData, latestData.pitch! * 180 / Math.PI);
                addData(setRollData, latestData.roll! * 180 / Math.PI);
                addData(setYawData, latestData.yaw! * 180 / Math.PI);
                addData(setFlapData, latestData.flapSensorPosition);
                addData(setAilLData, latestData.servoAileronL);
                addData(setAilRData, latestData.servoAileronR);
                addData(setElevData, latestData.servoElevator);
                addData(setRudData, latestData.servoRudder);
            }
        }, updateIntervalMS);

        return () => {
            clearInterval(intervalId);
        };
    }, []);

    const livePlotTickFormatter = (t) => `${Math.floor(t / 60000)}m ${Math.round((t % 60000) / 1000)}s`;
    const yTickFormatter = (t) => `${Math.round(t)}`

    // Memoized chart component to prevent unnecessary rerenders
    const LivePlotChartElement = memo(( props: { data: LivePlotDataPoint[], dataKey: string, yDomain?: any, log?: boolean}) => (
        // <div style={{ width: "100%", height: `${350}px` }}>
        <ResponsiveContainer width="100%" height={350}>
            <LineChart data={props.data} width={livePlotStyles.plotWidth} height={livePlotStyles.plotHeight} >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tickFormatter={livePlotTickFormatter}  />
                <YAxis name={props.dataKey} domain={props.yDomain ? props.yDomain : ['auto', 'auto']} scale={props.log ? "log" : "auto" } unit="&deg;" tickFormatter={yTickFormatter}/>
                <Line dataKey="value" stroke="red" name={props.dataKey} isAnimationActive={false}  dot={false}/>
                <Legend />
            </LineChart>
        </ResponsiveContainer>
    ));

    return (
        <div>
            <div style={livePlotRowStyle}>
                <div style={{ display: "flex", gap: "20px" }}>
                    {/* Assuming we don't need a domain to be above 90 for pitch */}
                    <LivePlotChartElement data={pitchData} dataKey="pitch_deg" yDomain={[-45, 45]} />  
                    <LivePlotChartElement data={rollData} dataKey="roll_deg" yDomain={[-45, 45]} />
                    <LivePlotChartElement data={yawData} dataKey="yaw_deg" /> 
                    <LivePlotChartElement data={flapData} dataKey="flapPosition" yDomain={[0, 45]} />
                </div>
            </div>
            <div style={livePlotRowStyle}>
                <div style={{ display: "flex", gap: "20px" }}>
                    <LivePlotChartElement data={ailLData} dataKey="ail_l" yDomain={[ServoMinMax.AILERON_PORT_MIN, ServoMinMax.AILERON_PORT_MAX]} />
                    <LivePlotChartElement data={ailRData} dataKey="ail_r" yDomain={[ServoMinMax.AILERON_SB_MIN, ServoMinMax.AILERON_SB_MAX]}/>
                    <LivePlotChartElement data={elevData} dataKey="elev" yDomain={[ServoMinMax.ELEVATOR_MIN, ServoMinMax.ELEVATOR_MAX]}/>
                    <LivePlotChartElement data={rudData} dataKey="rud" yDomain={[ServoMinMax.RUDDER_MIN, ServoMinMax.RUDDER_MAX]}/>
                </div>
            </div>
        </div>
    );
});
