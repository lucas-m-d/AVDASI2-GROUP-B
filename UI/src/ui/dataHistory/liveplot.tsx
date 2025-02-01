import { useState, useEffect, memo, useRef } from "react";
import { latestData } from "../../connection/connection";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

type  LivePlotDataPoint={
    "time":number|undefined
    "time_boot_ms":number|undefined;
    "time_boot_s":number|undefined;
    "flapPosition":number|undefined;
    "pitch_deg":number|undefined,
    "roll_deg":number|undefined

}


// const exampleData: LivePlotDataPoint[] = [ // example data generated by chatgpt
//     { time_boot_ms: 0, flapPosition: 0 },
//     { time_boot_ms: 100, flapPosition: 10 },
//     { time_boot_ms: 200, flapPosition: 20 },
//     { time_boot_ms: 300, flapPosition: 30 },
//     { time_boot_ms: 400, flapPosition: 40 },
//     { time_boot_ms: 500, flapPosition: 50 },
//     { time_boot_ms: 600, flapPosition: 60 },
//     { time_boot_ms: 700, flapPosition: 70 },
//     { time_boot_ms: 800, flapPosition: 80 },
//     { time_boot_ms: 900, flapPosition: 90 },
//   ];

export const LivePlotMemoized = memo(function LivePlot() {

    const [data, setData] = useState<LivePlotDataPoint[]>([])
    const loadTime = useRef(Date.now())
    const maxLength = 60*5

    useEffect(() => {
        const intervalId = setInterval(() => {
            
            
            // Ensure flapSensorPosition has a default value of 0 if it's undefined or null
            if (latestData.time_boot_ms !== undefined) {
                setData((oldData) => {
                    if (oldData.length > maxLength){
                        oldData.shift();
                    }
                    var newData: LivePlotDataPoint = {
                        "time":Date.now()-loadTime.current,
                        "time_boot_ms":latestData.time_boot_ms,
                        "time_boot_s":latestData.time_boot_ms!/1000,
                        "flapPosition":latestData.flapSensorPosition, // recharts deals with undefined by not plotting
                        "pitch_deg": latestData.pitch!*180/Math.PI,
                        "roll_deg": latestData.roll!* 180/Math.PI
                    }
                    return ([...oldData, newData])
            });
            }
            
        }, 1000/5); // Update interval at minimum required 5Hz for performance.  High-fidelity csv data is saved in the TMS directory

        return () => {
            clearInterval(intervalId)
            setData([])
        }
        }, [])
    
    
    

    return (
        <div>
            linechart here
            
                <LineChart
                    data={data}
                    width={500}
                    height={500}
                >

                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" tickFormatter={((val) => {
                        return Math.floor(val/60) + "m"+ Math.round(val%60) + "s"
                    })}/>
                    <YAxis name="Degrees"/>
                    <Line dataKey="flapPosition"/>
                    <Line dataKey="pitch_deg" stroke={"red"}/>
                    <Line dataKey="roll_deg" stroke={"green"}/>
                    <Legend />
                </LineChart>
            
            </div>
    )
})
