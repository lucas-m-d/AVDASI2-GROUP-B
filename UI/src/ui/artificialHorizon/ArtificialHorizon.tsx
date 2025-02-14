import React, {useRef, useEffect} from 'react';

// all values in degrees

const AHStyles = 
    {
        upper:"#4bb6ee",
        lower:"#642e0c",
        midLine:"white",
        midLineThickness:10,
        smallLineThickness:5,
        pitchLineResolution:2.5, // degrees between each line
        pitchRange:15, //+- current theta
        loadPitch:180,
        noDataFont: "30px Arial",
        noDataColor: "red"
    }

interface ArtificialHorizonProps {
    roll: number | undefined,
    pitch: number | undefined
}

export default function ArtificialHorizon ({roll, pitch}:ArtificialHorizonProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null)

    const height = window.innerWidth/3 - 15 

    const width = height - 100
    //var roll = roll * Math.PI/180;
    const barPadding = [0.42, 0.35, 0.275]
    const midTriangleWidth = 80
    const midTriangleHeight = 25
    const bankIndicator = {
        height: height * 0.6,
        radius: width*0.5,
        angleRange: Math.PI/6
    }
    
    
    useEffect(() => {
        // testing port here
        
        const canvas = canvasRef.current
        if (canvas) {
            const context = canvas?.getContext("2d")
            if (context){
                var displayRoll: number = 0;
                if (roll !== undefined){
                    displayRoll = roll!
                }

                var displayPitch: number = 0;
                if (pitch !== undefined){
                    displayPitch = (pitch! * 360 / (2 * Math.PI))
                }


                context.clearRect(0, 0, width, height);
                
                const yValuePerDegree = 0.5 * height / AHStyles.pitchRange
                const pitchY = displayPitch * yValuePerDegree
                context.translate(width / 2, height / 2);
                context.transform(Math.cos(displayRoll), -Math.sin(displayRoll), Math.sin(displayRoll), Math.cos(displayRoll), 0, 0)
                context.translate(-width / 2, -height / 2 + pitchY);
                
                const maxRotation =  4*Math.sqrt(width **2 + height **2);
                // background   
                context.fillStyle = AHStyles.upper
                context.fillRect((width-maxRotation)/2,(height-maxRotation)/2, maxRotation, maxRotation/2)
                context.fillStyle = AHStyles.lower
                context.fillRect((width-maxRotation)/2, height/2, maxRotation, maxRotation/2);
                context.fillStyle=AHStyles.midLine
                // context.fillRect(0,(height+pitchY/2-AHStyles.midLineThickness), width, AHStyles.midLineThickness)

                // horizontal lines
                //const lineDistanceY = 0.5*height / (AHStyles.pitchRange/AHStyles.pitchLineResolution)

                context.translate(0,-pitchY)
                context.strokeStyle = AHStyles.midLine
                context.font = "16px serif"
                              
                for (let alpha = Math.ceil((displayPitch+AHStyles.pitchRange)/AHStyles.pitchLineResolution) * AHStyles.pitchLineResolution; 
                    alpha >= displayPitch - AHStyles.pitchRange;
                    alpha -= AHStyles.pitchLineResolution) {
                        let y = yValuePerDegree * (displayPitch-alpha) + height/2 ;
                        if (alpha === 0) {
                            context.moveTo(width*-0.5, y)
                            context.lineTo(width*1.5, y)
                            context.lineWidth = AHStyles.smallLineThickness
                            context.stroke()
                            continue
                        }
                        context.beginPath();
                        let padding = (alpha%10 === 0) ?  barPadding[2] : (alpha%5 === 0 ? barPadding[1] : barPadding[0])
                        
                        context.moveTo(padding*width, y)
                        context.lineTo((1-padding)*width, y)
                        context.lineWidth = alpha%10 === 0 ? AHStyles.smallLineThickness : AHStyles.smallLineThickness*3/4;
                        if (padding !==barPadding[0]) {
                            context.fillText(alpha.toString() + "°", (padding - 0.05)*width, y)
                            context.fillText(alpha.toString() + "°", (1-padding + 0.05)*width, y)
                            
                        }
                        context.stroke()
                    } 
                    

                // draw FPA
                const fpaColour="#fefd00"
                context.resetTransform()
                
                // large triangle
                const largeFPAColour = "#7e7d00"
                context.fillStyle = largeFPAColour
                let path = new Path2D()
                path.moveTo((width-midTriangleWidth)/2, height/2)
                path.lineTo((width+midTriangleWidth)/2, height/2)
                path.lineTo(width/2, (height+midTriangleHeight)/2 + 10)
                context.fill(path)
                
                // small triangle

                context.fillStyle = fpaColour
                path = new Path2D()
                path.moveTo((width-midTriangleWidth)/2, height/2)
                path.lineTo((width+midTriangleWidth)/2, height/2)
                path.lineTo(width/2, (height+midTriangleHeight)/2)
                context.fill(path)
                
                // bars to the left and right
                context.lineWidth = 5 // AH stroke width
                context.strokeStyle = fpaColour
                context.beginPath();
                context.moveTo(width*0.3, height/2)
                context.lineTo(width*0.4, height/2)
                context.stroke()

                context.beginPath();
                context.moveTo(width*0.6, height/2)
                context.lineTo(width*0.7, height/2)
                context.stroke()

                // arc to show current angle
                context.beginPath()
                //context.strokeStyle = "white"
                context.arc(width*0.5, bankIndicator.height, bankIndicator.radius, -bankIndicator.angleRange - Math.PI/2, bankIndicator.angleRange - Math.PI/2  );
            
                // IF NO DATA AVAILABLE
                context.font = AHStyles.noDataFont;
                context.fillStyle = AHStyles.noDataColor;           
                (roll === undefined|| pitch === undefined ) && context.fillText("NO DATA\nAVAILABLE", 0, bankIndicator.height/2)
                
                context.stroke()
                context.save()
            }
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [roll, pitch])

    return (
    <div>
        <canvas id="gcs-artificial-horizon" ref={canvasRef} width={width} height={height} />
        {roll !== undefined ? (
                <p>Roll: {(roll! * 180 / Math.PI).toFixed(2)} deg</p>
            ) : (
                <p>No roll data available</p>
            )}
            
            {pitch !== undefined ? (
                <p>Pitch: {pitch!.toFixed(2)} deg</p>
            ) : (
                <p>No pitch data available</p>
        )}
    </div>
)
    
}