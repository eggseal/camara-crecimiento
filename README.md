# Camara de Crecimiento - SISE

## Architecture Diagram

```mermaid
flowchart 

subgraph Module["Module x2"]
    Sensors["Sensors"]
    ESP32["ESP32"]
    Actuators["Actuators"]
    Camera["RGB Camera"]

    Sensors --> ESP32
    ESP32 --> Actuators
end

subgraph RaspberryPi["Raspberry Pi"]
    RTMPClient["RTMP Client"]
    Python["Python"]

    Python <-- Serial --> ESP32
end

subgraph Nginx["NginX"]
    RTMPServer["RTMP Server :1935"]
    File[/"M3U8"/]
    HTTPServer["HTTP Server :5000"]

    RTMPServer --> File
    File --> HTTPServer
end

subgraph Datacenter["Virtual Machine"]
    Grafana["Grafana :3000"]
    NodeRed["NodeRed :1880"]
    Influx[("InfluxDB :8086")]
    SQL[("PostgreSQL" :5432)]
    Nginx

    NodeRed <-- TCP --> SQL
    NodeRed <-- HTTP --> Influx
    Grafana <-- HTTP --> NodeRed
end

User["User"]

%% ---------------- STREAM FLOW ----------------
Camera -- V4L2 --> RTMPClient
RTMPClient -- RTMP --> RTMPServer
RTMPServer -- RTMP --> Python

%% ---------------- DATA FLOW ----------------
NodeRed <-- MQTT, HTTP --> Python

%% ---------------- VISUALIZATION ----------------
HTTPServer -- HTTP --> Grafana
User <-- HTTP --> Grafana
```

## Entity-Relationship Diagram

```mermaid
erDiagram

    SENSOR_DATA {
        int experiment_id
        datetime timestamp
        float ambient_temperature
        float ambient_humidity
        float ambien_co2
        float soil_humidity
        float soil_temp
        float electric_conductivity
        float nitrogen
        float phosphorus
        float potassium
        float ph
        float white_light
        float uv_light
    }

    EXPERIMENT {
        int experiment_id
        int module_id
        string name
    }

    IMAGES {
        int experiment_id
        datetime timestamp
        string path
    }

    EXPERIMENT ||--o{ SENSOR_DATA : has
    EXPERIMENT ||--o{ IMAGES : has
```