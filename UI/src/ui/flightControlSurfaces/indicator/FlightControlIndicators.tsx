import HorizontalIndicator from "../shared/HorizontalIndicator";

interface FlightControlIndicatorsProps {
    ailL: number | undefined,
    ailR: number | undefined,
    elev: number | undefined,
    rud: number | undefined
}

export default function FlightControlIndicators ({ailL, ailR, elev, rud} : FlightControlIndicatorsProps) {

    

    return (
        <div>
            {/* aileron stuff*/}
            L Aileron
            <HorizontalIndicator id={"AileronL"} min={-100} max={100} current={ailL}/>
            R Aileron
            <HorizontalIndicator id={"AileronR"}min={-100} max={100} current={ailR}/>
            Elevator
            <HorizontalIndicator id={"elevatorPosition"}min={-100} max={100} current={elev}/>
            Rudder
            <HorizontalIndicator id={"rudderPosition"}min={-100} max={100} current={rud}/>
        </div>
    )
}