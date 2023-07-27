//Based from: https://techtutorialsx.com/2018/05/17/esp32-arduino-sending-data-with-socket-client/

#include <WiFi.h>
#include "esp_random.h"
#include <ArduinoJson.h>
 
const char* ssid = "PLDTHOMEFIBR_ESCALONA";
const char* password =  "anolacse00";
 
const uint16_t port = 8080;
const char * host = "192.168.2.252";
const String DEV_ID = "ESP32-001";
WiFiClient client;

const int ID_LIST_SIZE = 8;
const String IDS[ID_LIST_SIZE] =  { "4e69f87e9726ea66c866db38e21641e8",
                                "c33f6dbdcc7463113e99fe3ab26c1beb",
                                "9287a0e1ff6c0bf1fed593220292d265",
                                "d30a98f692a47c855474bc89ba619d29",
                                "e5a41f5a41e91569836609724c0606f1",
                                "b98a1b4e9ec6c478dd500d809b15060b",
                                "c4ad89d022ce28d543931549d3775966",
                                "e120f8723d42f52f916e816973802782"
                              }; //IDS is a mix of 1K.txt and 10K.txt

String getRandomStr(int len){
    String output = "";
    char* eligible_chars = "abcdef1234567890";
    for(int i = 0; i< len; i++){
        uint8_t random_index = random(0, strlen(eligible_chars));
        output += eligible_chars[random_index];
    }
    return output;
}

String getRandomID(){
  return IDS[random(0, ID_LIST_SIZE-1)];
}

void indicate(String id, String response){
  if (response == "ENTER"){ //ENTER
    Serial.println(id + ": ENTER");
  }else if(response == "EXIT"){ //EXIT
    Serial.println(id + ": EXIT");
  }else if(response == "ERROR"){ //LIMIT
    Serial.println(id + ": ERROR, TRY AGAIN");
  }else if(response == "LIMIT"){ //LIMIT
    Serial.println(id + ": LIMIT REACHED, TRY AGAIN LATER");
  }else if(response == "INVALID"){ //INVALID
    Serial.println(id + ": INVALID ID");
  }else{
    Serial.println("Response Unknown!");
  }
}

void rfid_simulator(WiFiClient client){
  String id = getRandomID(); //to be replaced with interrupt from rfid here
  String JSONString = "";
  DynamicJsonDocument doc(1024);
  doc["dev_id"] = DEV_ID;
  doc["cmd"] = "TAP";
  doc["val"] = id;
  serializeJson(doc, JSONString);

  //Serial.println(JSONString);
  client.print(JSONString);

  String rcv_str = "";
  DynamicJsonDocument rcvJSON(1024);
  while (client.available()) {
    rcv_str = client.readStringUntil('}');
    rcv_str += "}";
    deserializeJson(rcvJSON, rcv_str);
    if(rcvJSON.isNull()){
      Serial.println("Decoding JSON Response Failed!");
    }else{
      indicate(id, rcvJSON["val"]);
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