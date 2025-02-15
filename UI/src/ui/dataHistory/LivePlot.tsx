import { useState, useEffect, memo, useRef } from "react";
import CSS from "csstype";
import { latestData } from "../../connection/connection";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer } from 'recharts';

type  LivePlotDataPoint={
    "time":number|undefined
    "time_boot_ms":number|undefined;
    "time_boot_s":number|undefined;
    "flapPosition":number|undefined;
    "pitch_deg":number|undefined,
    "roll_deg":number|undefined,
    "yaw_deg":number|undefined,
    "ail_r":number|undefined,
    "ail_l":number|undefined,
    "elev":number|undefined,
    "rud":number|undefined

}

const livePlotStyles = {
    plotWidth: 500,
    plotHeight:500,
    rowHeight: "450px",
    
}
// const exampleData: LivePlotDataPoint[] = [
//     { time: 0, time_boot_ms: 0, time_boot_s: 0, flapPosition: 0, pitch_deg: 0, roll_deg: 0, yaw_deg: 0, ail_r: 0, ail_l: 0, elev: 0, rud: 0 },
//     { time: 1000, time_boot_ms: 1000, time_boot_s: 1, flapPosition: 5, pitch_deg: 1, roll_deg: -2, yaw_deg: 0.5, ail_r: 10, ail_l: -10, elev: 5, rud: 2 },
//     { time: 2000, time_boot_ms: 2000, time_boot_s: 2, flapPosition: 10, pitch_deg: 3, roll_deg: -1, yaw_deg: 1, ail_r: 20, ail_l: -20, elev: 10, rud: 4 },
//     { time: 3000, time_boot_ms: 3000, time_boot_s: 3, flapPosition: 15, pitch_deg: 5, roll_deg: 0, yaw_deg: 1.5, ail_r: 15, ail_l: -15, elev: 7, rud: 3 },
//     { time: 4000, time_boot_ms: 4000, time_boot_s: 4, flapPosition: 20, pitch_deg: 7, roll_deg: 1, yaw_deg: 2, ail_r: 5, ail_l: -5, elev: 3, rud: 1 },
//     { time: 5000, time_boot_ms: 5000, time_boot_s: 5, flapPosition: 25, pitch_deg: 8, roll_deg: 2, yaw_deg: 2.5, ail_r: 0, ail_l: 0, elev: 0, rud: 0 }
// ];


const livePlotRowStyle: CSS.Properties = {
        width:"inherit",
        height: livePlotStyles.rowHeight,
        overflowX: "auto",
        overflowY: "hidden",
        whiteSpace: "nowrap",
}
const updateIntervalMS = 1000/2
const maxDisplayTimeS = 120 // 2 minutes
const maxDataLength = maxDisplayTimeS*1E3/updateIntervalMS

export const LivePlotMemoized = memo(function LivePlot() {

    const [data, setData] = useState<LivePlotDataPoint[]>([])
    const loadTime = useRef(Date.now())
    useEffect(() => {
        const intervalId = setInterval(() => {
            // Ensure flapSensorPosition has a default value of 0 if it's undefined or null
            if (latestData.time_boot_ms !== undefined) { // if there is latest data
                setData((oldData) => {
                    if (oldData.length > maxDataLength){
                        oldData.shift();
                    }
                    var newData: LivePlotDataPoint = {
                        "time":Date.now()-loadTime.current,
                        "time_boot_ms":latestData.time_boot_ms,
                        "time_boot_s":latestData.time_boot_ms!/1000,
                        "flapPosition":latestData.flapSensorPosition, // recharts deals with undefined by not plotting
                        "pitch_deg": latestData.pitch!*180/Math.PI,
                        "roll_deg": latestData.roll!* 180/Math.PI,
                        "yaw_deg": latestData.yaw!*180/Math.PI,
                        "ail_l":latestData.servoAileronL!,
                        "ail_r":latestData.servoAileronR!,
                        "elev":latestData.servoElevator!,
                        "rud":latestData.servoRudder!                        
                        
                    }
                    return ([...oldData, newData])
            });
            }
            
        }, updateIntervalMS); // Update interval at 2Hz for performance.  High-fidelity csv data is saved in the TMS directory

        return () => {
            clearInterval(updateIntervalMS)
            setData([])
        }
        }, [])
    
    const livePlotTickFormatter = (t) => `${Math.floor(t / 60000)}m ${Math.round((t % 60000) / 1000)}s`
    
    const LivePlotChartElement = (props: {dataKey: string}) => {
        return(
        <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} width={livePlotStyles.plotWidth} height={livePlotStyles.plotHeight}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
                dataKey="time"
                tickFormatter={livePlotTickFormatter}
            />
            <YAxis name="Degrees" />
            <Line dataKey={props.dataKey} stroke="red" />
            <Legend />
        </LineChart>
        </ResponsiveContainer>
        )
    }
    return (
<div>
    <div
        style={livePlotRowStyle}
    >

    <div style={{ display: "flex", gap: "20px" }}>
        <LivePlotChartElement dataKey={"pitch_deg"} />
        <LivePlotChartElement dataKey={"roll_deg"} />
        <LivePlotChartElement dataKey={"yaw_deg"} />
        <LivePlotChartElement dataKey={"flapPosition"} />
    </div>
</div>
<div style={livePlotRowStyle}>
    <div style={{ display: "flex", gap: "20px" }}>
        <LivePlotChartElement dataKey="ail_l" />
        <LivePlotChartElement dataKey="ail_r" />
        <LivePlotChartElement dataKey="elev" />
        <LivePlotChartElement dataKey="rud" />
    </div>
</div>
</div>
    )
})
