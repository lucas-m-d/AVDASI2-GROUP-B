import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import TestArtificialHorizon from './artificialHorizon/testArtificialHorizon';
import { FlapControl } from './flightControlSurfaces/flaps/FlapControl';
import Grid from "@mui/material/Grid2"

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);


root.render(
  <React.StrictMode>
    <Grid container spacing={1}>
      <Grid size={6}>
        <TestArtificialHorizon />
      </Grid>
      <Grid size={3}>
      <FlapControl />
      </Grid>
      <Grid size={3}>
        
      </Grid>
    </Grid>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
