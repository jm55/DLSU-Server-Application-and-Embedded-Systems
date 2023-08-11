#include <SPI.h>
#include <MFRC522.h>
#include <driver/timer.h>
#include <ArduinoJson.h>
#include <WiFi.h>

#define SS_PIN  5  /*Slave Select Pin*/
#define RST_PIN 22  /*Reset Pin for RC522*/
#define LED_G   27   /*Pin 8 for LED*/
#define LED_R   12
#define LED_Y   14
#define BUTTON_PIN 34

MFRC522 mfrc522(SS_PIN, RST_PIN);   /*Create MFRC522 initialized*/
WiFiClient client;

timer_config_t config = {
.alarm_en = TIMER_ALARM_EN,
.counter_en = TIMER_PAUSE,
.intr_type = TIMER_INTR_LEVEL,
.counter_dir = TIMER_COUNT_UP,
.auto_reload = TIMER_AUTORELOAD_EN,
.divider = 80
};

int n1 = 1;
int n2 = 2;
String content = "";
String dev_id = "ESP_0";


char* ssid = "NSAPDEV";
char* password = "12345678";
char* server = "192.168.1.35";
const uint16_t port = 8081;
bool serverFlag = false;


StaticJsonDocument<200> cardInfo;
StaticJsonDocument<200> popReq;
StaticJsonDocument<200> popRes;
StaticJsonDocument<200> cardRes;

void button_isr(){ /*Thread 2 Hardware Interrupt Handler*/
  serverFlag = true;
}

static bool IRAM_ATTR timer0_isr_callback(void * args) { /*Thread 2 Timer Interrupt Handler*/
  serverFlag = true;
  return false;
}

void setup(){
  Serial.begin(115200);
  SPI.begin();

  /*Hardware setup*/          
  mfrc522.PCD_Init();   
  pinMode(LED_G, OUTPUT);  
  pinMode(LED_R, OUTPUT);  
  pinMode(LED_Y, OUTPUT);  
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), button_isr, RISING);

  /*WiFi setup*/
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connecting to WiFi");
    delay(500);
  }
  Serial.print("WiFi successfully connected. Device IP: ");
  Serial.println(WiFi.localIP());
  delay(2000);

  /*Server connection setup*/
  while(!client.connect(server, port)){
    Serial.println("Connection to server failed");
    delay(500);
  }
  Serial.println("Connection to server successful!");

  /*Threading setup*/
  xTaskCreate(cardHandler, "thread1", 4096, (void*)&n1, 1, NULL);
  xTaskCreate(serverResponseHandler, "thread2", 4096, (void*)&n2, 1, NULL);

  /*Thread 2 timer setup*/
  timer_init(TIMER_GROUP_0, TIMER_0, &config);
  timer_set_alarm_value(TIMER_GROUP_0, TIMER_0, 5000000); //us
  timer_start(TIMER_GROUP_0, TIMER_0);
  timer_isr_callback_add(TIMER_GROUP_0, TIMER_0, timer0_isr_callback, NULL, 0);


  Serial.print(dev_id);
  Serial.println(" is ready to start scanning");
}

void loop(){
}

void cardHandler(void *parameter){
  while(1){

    /*An RFID card was tapped*/
    if(mfrc522.PICC_IsNewCardPresent()){
      if(mfrc522.PICC_ReadCardSerial()){

        /*Read the RFID card's contents and build the JSON formatted string to be sent to the server*/
        Serial.println("CARD READ");
        Serial.print("UID tag: ");
        for (byte i = 0; i < mfrc522.uid.size; i++){
          content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
          content.concat(String(mfrc522.uid.uidByte[i], HEX));
        }
        Serial.println(content);
        cardInfo["dev_id"] = dev_id;
        cardInfo["cmd"] = "TAP";
        cardInfo["val"] = content;
        content = "";
        mfrc522.PICC_HaltA(); /*Stop scanning while the tapped card is present*/
        String send_str = "";
        serializeJson(cardInfo, send_str);

        /*Sending to server and receiving its response*/
        client.print(send_str);
        String rcv_str = "";
        while(!client.available()){
        }
        while(client.available()){
          rcv_str = client.readStringUntil('}');
          rcv_str.concat('}');
          deserializeJson(cardRes, rcv_str);
          if(cardRes.isNull()){
            Serial.println("Failed to decode the server's response");
            digitalWrite(LED_R, HIGH);
            vTaskDelay(1000/portTICK_PERIOD_MS);
            digitalWrite(LED_R, LOW);
          }
          else{
            String val = cardRes["val"];
            Serial.print("SERVER RESPONSE: ");
            Serial.println(val);
            /*Blink the appropriate LED for 1 second*/
            if(val == "ENTER"){
              digitalWrite(LED_G, HIGH);
              vTaskDelay(1000/portTICK_PERIOD_MS);
              digitalWrite(LED_G, LOW);
            }
            else if(val == "EXIT"){
              digitalWrite(LED_Y, HIGH);
              vTaskDelay(1000/portTICK_PERIOD_MS);
              digitalWrite(LED_Y, LOW);
            }
            else{
              digitalWrite(LED_R, HIGH);
              vTaskDelay(1000/portTICK_PERIOD_MS);
              digitalWrite(LED_R, LOW);
            }
            Serial.println("--------------------------------");
          }
        }
      }
    }

    /*Keep waiting for an RFID card to be tapped*/
    else{
      vTaskDelay(100/portTICK_PERIOD_MS);
    }
  }
}

void serverResponseHandler(void *parameter){
  while(1){
    if(serverFlag){
      popReq["dev_id"] = dev_id;
      popReq["cmd"] = "MON";
      popReq["val"] = "";
      String mon_str = "";
      String rcv_str = "";
      serializeJson(popReq, mon_str);
      client.print(mon_str);
      while(!client.available()){
      }
      while(client.available()){
        rcv_str = client.readStringUntil('}');
        rcv_str.concat('}');
        deserializeJson(popRes, rcv_str);
        if(popRes.isNull()){
          Serial.println("Failed to obtain a population update from the server");
        }
        else{
          String val = popRes["val"];
          Serial.println("SERVER POPULATION UPDATE");
          Serial.println(val);
        }
        Serial.println("--------------------------------");
      }
      serverFlag = false;
    }
    vTaskDelay(300/portTICK_PERIOD_MS);
  }
}