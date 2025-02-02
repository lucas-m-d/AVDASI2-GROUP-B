/***************************************************************\
*                        Basic Pressure Acquisition             *
* Author: Sid (we18336)                                         *
* Date: September 2023                                          *
*                                                               *
* Description:                                                  *
* This Arduino sketch sets up 12 analog read channels and       *
* outputs the readings to the serial monitor. It is designed    *
* for pressure acquisition using 12 MPXV7002DP sensors named    *
* P1 to P12, connected to analog pins A0 through A11,           *
* respectively.                                                 *
*                                                               *
* Hardware:                                                     *
*   - Arduino Board                                             *
*   - 12 MPXV7002DP Pressure Sensors (P1 to P12)                *
*   - Wiring:                                                   *
*     - P1 to A0                                                *
*     - P2 to A1                                                *
*     - P3 to A2                                                *
*     - P4 to A3                                                *
*     - P5 to A4                                                *
*     - P6 to A5                                                *
*     - P7 to A6                                                *
*     - P8 to A7                                                *
*     - P9 to A8                                                *
*     - P10 to A9                                               *
*     - P11 to A10                                              *
*     - P12 to A11                                              *
*                                                               *
* Software: None                                                *
*                                                               *
* License: MIT License                                          *
*                                                               *
* MIT License Summary:                                          *
* Permission is hereby granted, free of charge, to any person   *
* obtaining a copy of this software and associated              *
* documentation files (the "Software"), to deal in the          *
* Software without restriction, including without limitation    *
* the rights to use, copy, modify, merge, publish, distribute,  *
* sublicense, and/or sell copies of the Software, and to        *
* permit persons to whom the Software is furnished to do so,    *
* subject to the following conditions:                          *
*                                                               *
* The above copyright notice and this permission notice shall   *
* be included in all copies or substantial portions of the      *
* Software.                                                     *
*                                                               *
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY     *
* KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE    *
* WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR       *
* PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS   *
* OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR     *
* OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR   *
* OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE    *
* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.        *
\***************************************************************/

// Define constants for the number of sensors and analog pins
const int numSensors = 12;
const int analogPins[numSensors] = {A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11};
int sensorOffsets[numSensors];
int sensorReadings[numSensors];

void setup() {
  // Initialize Serial communication
  Serial.begin(19200); // Adjust the baud rate as needed

  // Wait for MATLAB to connect
  while (!Serial) {
    // Wait for the serial port to become ready
  }

  // Calculate and set individual sensor offsets to center readings at 512
  for (int i = 0; i < numSensors; i++) {
    sensorOffsets[i] = calculateOffset(analogPins[i]);
  }

  // Your additional setup code here
}

void loop() {
  int startTime = millis();
  // Read analog values for each sensor and apply individual offsets
  for (int i = 0; i < numSensors; i++) {
    sensorReadings[i] = analogRead(analogPins[i]) + sensorOffsets[i];
  }

  // Print sensor readings in the specified format
  for (int i = 0; i < numSensors; i++) {
    Serial.print(sensorReadings[i]); // Print the reading
    
    if (i == numSensors-1){
      Serial.print("\n");
      break;
      }
    Serial.print(",");
  }
  
  int endTime = millis();
  int executionTime = endTime - startTime;
  delay(20-executionTime); // 20ms delay for 50Hz (adjust as needed)
}

// Function to calculate individual sensor offsets
int calculateOffset(int pin) {
  int sum = 0;
  const int numReadings = 10;

  // Take 10 readings and calculate the average
  for (int i = 0; i < numReadings; i++) {
    sum += analogRead(pin);
    delay(10); // Delay between readings (adjust as needed)
  }

  int averageReading = sum / numReadings;

  // Calculate and return the offset to center readings at 512
  return 512 - averageReading;
}
