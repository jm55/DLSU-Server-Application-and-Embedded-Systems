//Based from: https://techtutorialsx.com/2018/05/17/esp32-arduino-sending-data-with-socket-client/

#include <WiFi.h>
#include "esp_random.h"
 
const char* ssid = "PLDTHOMEFIBR_ESCALONA";
const char* password =  "anolacse00";
 
const uint16_t port = 8080;
const char * host = "192.168.2.252";
WiFiClient client;

String getRandomStr(int len){
    String output = "";
    char* eligible_chars = "abcdef1234567890";
    for(int i = 0; i< len; i++){
        uint8_t random_index = random(0, strlen(eligible_chars));
        output += eligible_chars[random_index];
    }
    return output;
}

void rfid_simulator(WiFiClient client){
  String id = getRandomStr(32); //to be replaced with interrupt from rfid here
  client.print(id);
  String rcv_str = "";
  while (client.available()) {
    char rcv = client.read();
    if(rcv != '\n')
      rcv_str += char(rcv);
    if (rcv_str == "ENTER"){ //ENTER
      Serial.println(id + ": ENTER");
      rcv_str = "";
    }else if(rcv_str == "EXIT"){ //EXIT
      Serial.println(id + ": EXIT");
      rcv_str = "";
    }else if(rcv_str == "ERROR"){ //Error
      Serial.println(id + ": ERROR, TRY AGAIN");
      rcv_str = "";
    }
  }
  client.stop();
  delay(1000);
}

void setup()
{
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
  delay(5000); //5s delay

  while(!client.connect(host, port)) {
      Serial.println("Connection to host failed");
      delay(1000);
  }
  Serial.println("Connected to server successful!");
}
 
void loop()
{
    rfid_simulator(client);
}