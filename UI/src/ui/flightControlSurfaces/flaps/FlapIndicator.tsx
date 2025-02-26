import React, { useRef, useEffect } from "react";

interface flapIndicatorProps {
    min: number,
    max: number,
    request?: number,
    position: [number?, number?]
}

const FlapIndicatorStyle = {
    lineHeight: 10,
    backgroundColor: "#E0E0E0",
    requestColor: "blue",
    positionColor:"blue",
    positionOverflowColor: "red",
    triangleWidth:10,
    triangleHeight:5
}

export default function FlapIndicator({min, max, request, position}:flapIndicatorProps){
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const width=250
    const height=250
    const proportions = [3, 3, 3, 3, 3] // LEFT, SPACE, CENTER, SPACE, RIGHT
    const proportionSum = proportions.reduce((sum, x) => sum + x, 0)

    var xPositions: Array<number> = [];
    var indicatorWidths = proportions.map(x=> x*width/proportionSum )
    var indicatorHeight = height*0.9
    var proportionLoopSum = 0
    

    for (let i=0; i<proportions.length; i++){
        if (!proportions[i-1]) {
            xPositions = [0]
            continue;
        }
        proportionLoopSum += proportions[i]
        xPositions = [...xPositions, width*proportionLoopSum/proportionSum]
    }

    request = Number(request);
    position = [Number(position[0]), Number(position[1])]

    useEffect(() => {
        
        const canvas = canvasRef.current
        if (canvas) {
            const context = canvas?.getContext("2d")
            if (context){
                context.clearRect(0, 0, width, height);
                //context.translate(0, height/2)

                // create a background rectangle 
                context.fillStyle=FlapIndicatorStyle.backgroundColor
                context.fillRect(xPositions[0], 0, indicatorWidths[0], indicatorHeight)
                context.fillRect(xPositions[2], 0, indicatorWidths[2], indicatorHeight)                
                context.fillRect(xPositions[4], 0, indicatorWidths[4], indicatorHeight)

                // left and right
                if (Number(position[0]) > max){
                    /// if it's going to overflow
                    context.fillStyle=FlapIndicatorStyle.positionOverflowColor
                    context.fillRect(xPositions[0],0, indicatorWidths[0], indicatorHeight)
                } else {
                    context.fillStyle=FlapIndicatorStyle.positionColor
                    context.fillRect(xPositions[0],0, indicatorWidths[0], indicatorHeight*position[0]!/max)
                }

                if (Number(position[1]) > max){
                    /// if it's going to overflow
                    context.fillStyle=FlapIndicatorStyle.positionOverflowColor
                    context.fillRect(xPositions[4],0, indicatorWidths[4], indicatorHeight)
                } else {
                    context.fillStyle=FlapIndicatorStyle.positionColor
                    context.fillRect(xPositions[4],0, indicatorWidths[4], indicatorHeight*position[1]!/max)
                }

                

                // requested
                context.fillStyle=FlapIndicatorStyle.requestColor
                context.fillRect(xPositions[2],0, indicatorWidths[2], indicatorHeight*request!/max)

                // text below markers
                context.textAlign="center"
                context.textBaseline = 'bottom';
                context.font = '15pt Calibri';
                context.fillStyle = 'black';
                context.fillText("L", xPositions[0] + indicatorWidths[0]/2, height)
                context.fillText("REQ", xPositions[2] + indicatorWidths[2]/2, height)  
                context.fillText("R", xPositions[4] + indicatorWidths[4]/2, height)
                

                context.save()
            }
        }
    })
    return (
        <canvas id="flap-indicator" ref={canvasRef} width={width} height={height} />
    )
}