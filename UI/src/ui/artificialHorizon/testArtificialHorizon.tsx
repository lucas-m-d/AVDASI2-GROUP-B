import React, {useState, useEffect} from 'react';
import ArtificialHorizon from './ArtificialHorizon';


export default function TestArtificialHorizon () {
    const [roll, setRoll] = useState(0);   // Roll state
    const [pitch, setPitch] = useState(0); // Pitch state
  
    useEffect(() => {
      const fps = 20; // 20 frames per second
      const interval = 1000 / fps; // 50ms per frame
  
      let time = 0; // Time variable to control the sinusoidal motion
  
      const intervalId = setInterval(() => {
        const speedFactor = 0.02;  // Controls the speed of the oscillation
  
        // Oscillate roll between -30 and 30 degrees
        const newRoll = 15 * Math.sin(time * speedFactor);
        setRoll(newRoll);
  
        // Oscillate pitch between -45 and 45 degrees
        const newPitch = 15 * Math.sin(time * speedFactor*1.1);
        setPitch(newPitch);
  
        time += 1; // Increment time to move the oscillation forward
      }, interval);
  
      // Cleanup interval on component unmount
      return () => clearInterval(intervalId);
    }, []);
  
    return (
      <ArtificialHorizon roll={roll} pitch={pitch} />
    );
  }