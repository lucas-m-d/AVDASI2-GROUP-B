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
            <HorizontalIndicator id={"AileronL"} min={-30} max={30} current={ailL}/>
            R Aileron
            <HorizontalIndicator id={"AileronR"}min={-30} max={30} current={ailR}/>
            Elevator
            <HorizontalIndicator id={"elevatorPosition"} min={-45} max={45} current={elev}/>
            Rudder
            <HorizontalIndicator id={"rudderPosition"}min={-40} max={40} current={rud}/>
        </div>
    )
}