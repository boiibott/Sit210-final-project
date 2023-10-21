#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <ThingSpeak.h>
#include <WiFi.h> // Include the WiFi library

// ThingSpeak settings
char thingSpeakApiKey[] = "JJQGKS8WQN5SGTU2";
const char* ssid = "M30s";
const char* password = "vcvw3532";
int CHANNEL_ID = 2300332; // Replace with your ThingSpeak channel ID

// Initialize sensors
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
const int ecgPin = A0;
const int pulsePin = A1;
int threshold = 550; // Adjust this threshold according to your sensor and environment
boolean pulseDetected = false;
unsigned long lastPulseTime = 0;
int pulseRate = 0;

// Create a WiFiClient instance
WiFiClient client;

void setup() {
  Serial.begin(9600);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize ThingSpeak with the WiFiClient instance
  ThingSpeak.begin(client);
}

void loop() {
  // Read data from the sensors
  float ecgData = readECGData();
  float tempData = mlx.readObjectTempC();
  int pulseData = readPulseData();

  // Send data to ThingSpeak
  ThingSpeak.setField(1, ecgData);
  ThingSpeak.setField(2, tempData);
  ThingSpeak.setField(3, pulseData);

  int status = ThingSpeak.writeFields(CHANNEL_ID, thingSpeakApiKey);

  if (status == 200) {
    Serial.println("Data sent to ThingSpeak successfully.");
  } else {
    Serial.println("Failed to send data to ThingSpeak. Status code: " + String(status));
  }

  delay(5000);  // Send data every 15 seconds
}

float readECGData() {
  int ecgValue = analogRead(ecgPin);
  // Process the ECG value here, e.g., send it to ThingSpeak or display it
  Serial.println("ECG Value: " + String(ecgValue));
  // Add some delay to control the sampling rate
  delay(1000);
  return ecgValue;
}

int readPulseData() {
  int rawValue = analogRead(pulsePin);
  // Perform signal processing to extract pulse rate from rawValue
  int pulseRate = calculatePulseRate(rawValue);
  return pulseRate;
}

int calculatePulseRate(int rawValue) {
  if (rawValue > threshold && !pulseDetected) {
    // Pulse detected
    pulseDetected = true;
    unsigned long currentTime = millis();
    unsigned long timeSinceLastPulse = currentTime - lastPulseTime;
    lastPulseTime = currentTime;
    // Calculate pulse rate in beats per minute (BPM)
    pulseRate = 60000 / timeSinceLastPulse;
  }

  if (rawValue <= threshold && pulseDetected) {
    // Pulse ended
    pulseDetected = false;
  }

  delay(1000);
  return pulseRate;
}
