#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <MFRC522.h>
#include <SPI.h>

#define RST_PIN         D3
#define SS_PIN          D4

MFRC522 mfrc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;
MFRC522::StatusCode status;

const char* ssid = "realme X2";
const char* password = "e^ipi=-1";
const char* host = " 192.168.94.252";  // Change to the IP address of your Python server
unsigned int localPort = 8888;  // Change the port number

WiFiUDP udp;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  udp.begin(localPort);
  mfrc522.PCD_Init();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println(F("Read personal data on a MIFARE PICC:"));
}

void loop() {
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;

  byte block;
  byte len;
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  Serial.println(F("Card Detected:"));

  byte buffer1[18];

  block = 1;
  len = 18;

  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, 1, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Authentication failed: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }

  status = mfrc522.MIFARE_Read(block, buffer1, &len);
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Reading failed: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }
  char studentID[14];
  for (uint8_t i = 0; i < 13; i++) {
    studentID[i] = (char)buffer1[i];
  }
  for (uint8_t i = 0; i < 13; i++) {
    Serial.print(studentID[i]);
  }
  Serial.println();
  studentID[14] = '\0';
  udp.beginPacket(host, localPort);
  udp.write(studentID);
  udp.endPacket();
  delay(1000); // Send a message every second
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}
