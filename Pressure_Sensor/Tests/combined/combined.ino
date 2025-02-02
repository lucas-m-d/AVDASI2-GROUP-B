#include <Arduino.h>
#include <I2C_Slave.h>

#define I2C_ADDR 0x09  // Unused I2C address
#define SERIAL_BAUD 115200

const int numSensors = 12;
const int analogPins[numSensors] = {A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11};
int sensorOffsets[numSensors];
int sensorReadings[numSensors];

#define GET_NUM_PINS 0xFE
#define SET_PIN_INDEX 0xFF

#ifdef ESP32  // board compatibility
static const uint8_t A1 = 34;
static const uint8_t A2 = 35;
#endif

uint32_t num_errors = 0;
const int err_value = -1;

void command_handler(uint8_t command, uint8_t value) {
    switch (command) {
        case GET_NUM_PINS:
            Slave.writeRegisters(numSensors);
            Serial.println(F("Pin count requested."));
            break;
        case SET_PIN_INDEX:
            if (value < numSensors) {
                int reading = analogRead(analogPins[value]);
                Slave.writeRegisters(static_cast<uint32_t>(reading)); // Send as 16-bit value
            } else {
                Slave.writeRegisters(static_cast<uint32_t>(err_value));
            }
            break;
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    Slave.begin(I2C_ADDR);
    Slave.onCommand(command_handler);

    Serial.print(F("\nSlave address    : 0x"));
    if (I2C_ADDR < 0x10) Serial.print('0');
    Serial.println(I2C_ADDR, HEX);
    Serial.print("Analog pin count : ");
    Serial.println(numSensors);

    for (int i = 0; i < numSensors; i++) {
        sensorOffsets[i] = calculateOffset(analogPins[i]);
    }

    Serial.println(F("\nInitialization complete."));
}

void loop() {
    int startTime = millis();
    for (int i = 0; i < numSensors; i++) {
        sensorReadings[i] = analogRead(analogPins[i]) + sensorOffsets[i];
    }

    Serial.print(F("Sensor Readings: "));
    for (int i = 0; i < numSensors; i++) {
        Serial.print(sensorReadings[i]);
        if (i < numSensors - 1) Serial.print(", ");
    }
    Serial.println();

    uint32_t e = Slave.numErrors();
    if (num_errors != e) {
        num_errors = e;
        Serial.print(F("I2C communication error count: "));
        Serial.println(num_errors);
    }
    
    int executionTime = millis() - startTime;
    delay(max(20 - executionTime, 1));  // Ensures 50Hz sampling rate
}

int calculateOffset(int pin) {
    int sum = 0;
    const int numReadings = 10;
    for (int i = 0; i < numReadings; i++) {
        sum += analogRead(pin);
        delay(10);
    }
    return 512 - (sum / numReadings);
}
