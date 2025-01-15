import { useRef, useEffect } from "react";

interface HorizontalIndicatorProps{
    min: number,
    max: number,
    current: number | undefined,
    id: string,
    width?: number | "100%", // px
    height?: number // px
}

const HorizontalIndicatorStyle = {
    backgroundColor: "#E0E0E0",
    undefinedColor: "yellow",
    positionColor:"red",
    textColor: "black",
    font: "175% sans-serif",
    lineWidth: 4

}

export default function HorizontalIndicator ({min, max, current, id, width, height} : HorizontalIndicatorProps){
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const canvas = canvasRef.current

    width = width ? width : "100%";
    height = height ? height : 70;

    useEffect(() => {
        const canvas = canvasRef.current
        if (canvas){
            const context = canvas?.getContext("2d")
            if (context) {
                var canvasWidth = document.getElementById(id)!.getBoundingClientRect().width;

                context.clearRect(0, 0, canvasWidth!, height!);

                context.fillStyle = HorizontalIndicatorStyle.backgroundColor

                context.fillRect(0,0,canvasWidth!, height!) // fill background

                
                if (current) {
                    // start in the middle
                    const percentFull = current / (max - min);
                    context.fillStyle = HorizontalIndicatorStyle.positionColor
                    context.fillRect(canvasWidth!/2, 0, percentFull*canvasWidth!, height!) // draw current position rectangle
                    // draw text in middle
                    context.textAlign = "center";
                    context.textBaseline = "middle"
                    context.fillStyle = HorizontalIndicatorStyle.textColor
                    context.font = HorizontalIndicatorStyle.font
                    context.fillText(current.toString(), canvasWidth!/2, height!/2, 100)
                } else {
                    context.strokeStyle= HorizontalIndicatorStyle.undefinedColor
                    context.lineWidth = HorizontalIndicatorStyle.lineWidth
                    // draw a cross
                    context.moveTo(0,0)
                    context.lineTo(canvasWidth, height!)
                    context.moveTo(canvasWidth, 0)
                    context.lineTo(0, height!)

                    context.stroke()
                }
                
                context.save()
            }
            
        }
    })

    return (
        <div style={{display: "flex", justifyContent: "center", alignItems: "center"}}>
            <canvas ref={canvasRef} id={id} style={{width:width!, height: height!}} />
        </div>
    )
}