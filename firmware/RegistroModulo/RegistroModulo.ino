#include <EEPROM.h>

#define ADDRESS 0x0

void setup() {
    Serial.begin(115200);
    Serial.print("Enter the number ID (1-256): ");
}

void loop() {
    if (!Serial.available()) return;
    int input = Serial.parseInt();

    if (input < 1 || input > 256) {
        Serial.println("Invalid value.");
        return;
    }

    byte value = input - 1;
    EEPROM.update(ADDRESS, value);
    Serial.println("Value stored.");
}