#include <Preferences.h>

Preferences preferences;

uint8_t id = 0;

void setup() {
    Serial.begin(115200);
    preferences.begin("module");
    id = preferences.getUChar("id");
    Serial.printf("Module registered with ID [%d]\n", id);

    Serial.println("Enter a number to change the module ID: (1-256): ");
}

void loop() {
    if (!Serial.available()) return;
    int input = Serial.parseInt();

    if (input < 0x01 || input > 0xFF) {
        Serial.println("Invalid value.");
        return;
    }

    id = input;
    preferences.putUChar("id", id);
    Serial.printf("Value stored in module.id [%d]\n", id);
    ESP.restart();
}