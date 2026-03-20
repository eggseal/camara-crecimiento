// Libraries
#include <Preferences.h>
#include <ArduinoJson.h>

// Constants
#define SerialX Serial

// Variables
uint8_t moduleID = 0;

// Library initialization
Preferences preferences;
JsonDocument data;

// Subroutines
void serialEvent() {
    if (!SerialX.available()) return;
    data.clear();
    DeserializationError error = deserializeJson(data, SerialX.readStringUntil('\n'));

    if (error) {
        data["id"] = moduleID;
        data["error"] = error.c_str();
        serializeJson(data, SerialX);
        SerialX.println();
        return;
    }

    uint8_t cmd = data["cmd"];
    data.clear();

    switch(cmd) {
        case 1:
            data["id"] = moduleID;
            data["temp"] = random(0, 100);
            serializeJson(data, SerialX);
            SerialX.println();
            break;
    }
}

void setup() {
    preferences.begin("module");
    moduleID = preferences.getUChar("id");
    if (moduleID == 0) exit(0);

    SerialX.begin(115200);
}

void loop() {
    
}