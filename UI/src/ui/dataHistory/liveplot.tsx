import React, { useEffect, useState, useRef } from "react";
import { Line } from "react-chartjs-2";
import { Chart, ChartOptions, LinearScale, CategoryScale, Title, Tooltip, Legend } from "chart.js";
import "chart.js/auto"; // Import Chart.js components
import { latestData } from "../../connection/connection";

// Register only the components necessary for line charts
Chart.register(LinearScale, CategoryScale, Title, Tooltip, Legend);

export default function LivePlot() {
    const chartRef = useRef<Chart | null>(null);

    // State for chart data
    const [data, setData] = useState({
        labels: [] as string[], // Typed as string array
        datasets: [
            {
                label: "Angle (degrees)",
                data: [] as number[], // Typed as number array
                fill: false,
                backgroundColor: "rgba(75,192,192,1)",
                borderColor: "rgba(75,192,192,1)",
            },
        ],
    });

    const options: ChartOptions<'line'> = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                type: "linear", // Explicitly set type as "linear" for the x-axis
                position: "bottom",
            },
            y: {
                type: "linear", // Explicitly set type as "linear" for the y-axis
                beginAtZero: true,
                title: {
                    display: true,
                    text: "Angle (°)",
                },
            },
        },
    };

    useEffect(() => {
        const intervalId = setInterval(() => {
            const now = new Date().toISOString();
            const angle = latestData.flapSensorPosition || 0;

            // Safely update chart data with proper types and limit to 20 points
            setData((prevData) => {
                const newLabels = [...prevData.labels, now].slice(-20); // Limit to 20 points
                const newData = [...prevData.datasets[0].data, angle].slice(-20); // Limit to 20 points

                return {
                    ...prevData,
                    labels: newLabels,
                    datasets: [
                        {
                            ...prevData.datasets[0],
                            data: newData,
                        },
                    ],
                };
            });
        }, 1000 / 20); // Update at 20 Hz

        return () => clearInterval(intervalId);
    }, []); // Empty dependency array, so it only runs on mount

    return (
        <div style={{ height: "300px", width: "100%", position: "relative" }}>
            <Line ref={chartRef} data={data} options={options} />
        </div>
    );
}
