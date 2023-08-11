#include <driver/timer.h>
#include <driver/gpio.h>
#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>

#define RST_PIN 22           
#define SS_PIN 5           
#define IRQ_PIN 2           

timer_config_t config = {
.alarm_en = TIMER_ALARM_EN,
.counter_en = TIMER_PAUSE,
.intr_type = TIMER_INTR_LEVEL,
.counter_dir = TIMER_COUNT_UP,
.auto_reload = TIMER_AUTORELOAD_EN,
.divider = 80
};


MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.


String cardByte, cardAscii;
bool rfidFlag = false;
bool serverFlag = false;
byte regVal = 0x7F;
int n1 = 1;
int n2 = 2;
String dev_id = "ESP1"; //Different for each ESP
StaticJsonDocument<200> cardJson;

/*The function sending to the MFRC522 the needed commands to activate the reception*/
void activateRec(MFRC522 mfrc522) {
  mfrc522.PCD_WriteRegister(mfrc522.FIFODataReg, mfrc522.PICC_CMD_REQA);
  mfrc522.PCD_WriteRegister(mfrc522.CommandReg, mfrc522.PCD_Transceive);
  mfrc522.PCD_WriteRegister(mfrc522.BitFramingReg, 0x87);
}

/*The function to clear the pending interrupt bits after interrupt serving routine*/
void clearInt(MFRC522 mfrc522) {
  mfrc522.PCD_WriteRegister(mfrc522.ComIrqReg, 0x7F);
}

/*MFRC522 interrupt serving routine*/
void readCard() {
  Serial.println("ISR");
  rfidFlag = !rfidFlag;
}

/*Timer interrupt serving routine*/
static bool IRAM_ATTR timer0_isr_callback(void * args) { //DHT
  serverFlag = !serverFlag;
  return false;
}

void setup() {
  Serial.begin(115200); 
  SPI.begin();
  mfrc522.PCD_Init(); // Init MFRC522 card

  /* setup the IRQ pin*/

  /*
   * Allow the ... irq to be propagated to the IRQ pin
   * For test purposes propagate the IdleIrq and loAlert
   */

  /*Activate the interrupt*/

  /*Thread 2 timer setup*/
  timer_init(TIMER_GROUP_0, TIMER_0, &config);
  timer_set_alarm_value(TIMER_GROUP_0, TIMER_0, 500000); //us
  timer_start(TIMER_GROUP_0, TIMER_0);
  timer_isr_callback_add(TIMER_GROUP_0, TIMER_0, timer0_isr_callback, NULL, 0);

  /*Threading setup*/
  //xTaskCreate(cardHandler, "thread1", 1024, (void*)&n1, 1, NULL);
  //xTaskCreate(serverStatHandler, "thread2", 1024, (void*)&n2, 1, NULL);
}

void loop() {
  if(!mfrc522.PICC_ReadCardSerial()){
    return;
  }
  else{
      Serial.print(F("Card UID:"));
      byteToAscii(mfrc522.uid.uidByte, mfrc522.uid.size);
      Serial.println();

        /*Building the JSON with the RFID card information, to be sent to the server*/
      cardJson["dev_id"] = dev_id;
      cardJson["cmd"] = "TAP";
      cardJson["val"] = cardAscii;
      }
} 

void cardHandler(void *parameter) {
  while(1){
     //new read interrupt
      //read the tag data
      // Show some details of the PICC (that is: the tag/card)
      if(!mfrc522.PICC_ReadCardSerial()){
      }
      else{
        Serial.print(F("Card UID:"));
        byteToAscii(mfrc522.uid.uidByte, mfrc522.uid.size);
        Serial.println();

        /*Building the JSON with the RFID card information, to be sent to the server*/
        cardJson["dev_id"] = dev_id;
        cardJson["cmd"] = "TAP";
        cardJson["val"] = cardAscii;
      }
      
      //TODO: send to server
  // The receiving block needs regular retriggering (tell the tag it should transmit??)

    vTaskDelay(50/portTICK_PERIOD_MS);
  }
}


void serverStatHandler(void *parameter) {
  while (1){
    if(serverFlag){
      //TODO:
      //query server
      //parse server response
      //print to serial
    }
  }
}

/*Helper routine to dump a byte array as hex values then converts to ASCII.*/
void byteToAscii(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++){
     cardByte.concat(String(buffer[i] < 0x10 ? "0" : ""));
     cardByte.concat(String(buffer[i], HEX));
  }

  for (int i = 0; i < cardByte.length(); i += 2){
    char val = cardByte[i] > 0x39 ? (cardByte[i] - 'A') * 16 : (cardByte[i] - '0') * 16;
    val += cardByte[i+1] > 0x39 ? (cardByte[i+1] - 'A') : (cardByte[i+1] - '0');
    cardAscii.concat(val); 
  }

  Serial.println(cardByte);
  Serial.print("Ascii: ");
  Serial.println(cardAscii);
}