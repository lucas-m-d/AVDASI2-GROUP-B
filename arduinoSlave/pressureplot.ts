import React, { useState, useEffect } from "react";
import Plot from "react-plotly.js";
import io from "socket.io-client"; // Assuming your GCS sends data over socket.io

const PressureGraph = () => {
  const [pressureData, setPressureData] = useState([]);
  const [coefficients, setCoefficients] = useState([]);

  useEffect(() => {
    // Connect to your GCS WebSocket server
    const socket = io("ws://your-gcs-server-address");

    socket.on("pressureData", (data) => {
      // Assuming the data is an array of pressure values from your sensors
      const updatedPressureData = data.map((value) => {
        // Convert pressure data (adjust your formula if needed)
        return 1000 * ((5 / 1023) * value - 2.5);
      });

      setPressureData(updatedPressureData);

      const updatedCoefficients = updatedPressureData.map((pressure) => {
        // Calculate coefficients (adjust the formula based on your requirements)
        return pressure / ((1.225 * 50 ** 2) / 2); // example calculation
      });

      setCoefficients(updatedCoefficients);
    });

    // Clean up the WebSocket connection when the component is unmounted
    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div>
      <h1>Pressure Sensor Data</h1>
      <Plot
        data={[
          {
            x: Array.from({ length: pressureData.length }, (_, i) => i + 1), // X-axis: data index
            y: pressureData,
            type: "scatter",
            mode: "lines+markers",
            marker: { color: "red" },
            name: "Pressure Data",
          },
          {
            x: Array.from({ length: coefficients.length }, (_, i) => i + 1),
            y: coefficients,
            type: "scatter",
            mode: "lines+markers",
            marker: { color: "blue" },
            name: "Coefficients",
          },
        ]}
        layout={{
          title: "Pressure Sensor Data and Coefficients",
          xaxis: {
            title: "Sensor Reading Index",
          },
          yaxis: {
            title: "Pressure (Pa)",
          },
        }}
      />
    </div>
  );
};

export default PressureGraph;
