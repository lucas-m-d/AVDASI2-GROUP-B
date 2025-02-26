import HorizontalIndicator from "../shared/HorizontalIndicator";

import { ServoMinMax } from "../../../servoMinMax";

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
            <HorizontalIndicator id={"AileronL"} min={ServoMinMax.AILERON_PORT_MIN} max={ServoMinMax.AILERON_PORT_MAX} current={ailL}/>
            R Aileron
            <HorizontalIndicator id={"AileronR"}min={ServoMinMax.AILERON_SB_MIN} max={ServoMinMax.AILERON_SB_MAX} current={ailR}/>
            Elevator
            <HorizontalIndicator id={"elevatorPosition"} min={ServoMinMax.ELEVATOR_MIN} max={ServoMinMax.ELEVATOR_MAX} current={elev}/>
            Rudder
            <HorizontalIndicator id={"rudderPosition"}min={ServoMinMax.RUDDER_MIN} max={ServoMinMax.RUDDER_MAX} current={rud}/>
        </div>
    )
}