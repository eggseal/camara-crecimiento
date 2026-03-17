#include <Preferences.h>

Preferences preferences;

uint8_t moduleID = 0;

void setup() {
    preferences.begin("module");
    id = preferences.getUChar("id");
    if (id == 0) {
        Serial.println("This device is not registered with a Module ID.");
        exit(0);
    }
}

void loop() {
    
}