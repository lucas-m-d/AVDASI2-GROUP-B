import React, { useState } from "react";
import { dataHistory } from "../../connection/connection";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

setTimeout(() => {
    console.log(dataHistory)
}, 1000)

export default function AttitudeGraph () {    
    
    return (
        <ResponsiveContainer>
            <LineChart
            data={dataHistory}
            >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time_boot_ms" />
                <YAxis dataKey="roll" />
            </LineChart>
        </ResponsiveContainer>
    )
}