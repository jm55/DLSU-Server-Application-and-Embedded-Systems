/*
 * --------------------------------------------------------------------------------------------------------------------
 * Example sketch/program showing how to read data from a PICC to serial.
 * --------------------------------------------------------------------------------------------------------------------
 * This is a MFRC522 library example; for further details and other examples see: https://github.com/miguelbalboa/rfid
 * 
 * Example sketch/program showing how to read data from a PICC (that is: a RFID Tag or Card) using a MFRC522 based RFID
 * Reader on the Arduino SPI interface.
 * 
 * When the Arduino and the MFRC522 module are connected (see the pin layout below), load this sketch into Arduino IDE
 * then verify/compile and upload it. To see the output: use Tools, Serial Monitor of the IDE (hit Ctrl+Shft+M). When
 * you present a PICC (that is: a RFID Tag or Card) at reading distance of the MFRC522 Reader/PCD, the serial output
 * will show the ID/UID, type and any data blocks it can read. Note: you may see "Timeout in communication" messages
 * when removing the PICC from reading distance too early.
 * 
 * If your reader supports it, this sketch/program will read all the PICCs presented (that is: multiple tag reading).
 * So if you stack two or more PICCs on top of each other and present them to the reader, it will first output all
 * details of the first and then the next PICC. Note that this may take some time as all data blocks are dumped, so
 * keep the PICCs at reading distance until complete.
 * 
 * @license Released into the public domain.
 * 
 * Typical pin layout used:
 * -----------------------------------------------------------------------------------------
 *             MFRC522      Arduino       Arduino   Arduino    Arduino          Arduino
 *             Reader/PCD   Uno/101       Mega      Nano v3    Leonardo/Micro   Pro Micro
 * Signal      Pin          Pin           Pin       Pin        Pin              Pin
 * -----------------------------------------------------------------------------------------
 * RST/Reset   RST          9             5         D9         RESET/ICSP-5     RST
 * SPI SS      SDA(SS)      10            53        D10        10               10
 * SPI MOSI    MOSI         11 / ICSP-4   51        D11        ICSP-4           16
 * SPI MISO    MISO         12 / ICSP-1   50        D12        ICSP-1           14
 * SPI SCK     SCK          13 / ICSP-3   52        D13        ICSP-3           15
 *
 * More pin layouts for other boards can be found here: https://github.com/miguelbalboa/rfid#pin-layout
 */

#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN  5  /*Slave Select Pin*/
#define RST_PIN 22  /*Reset Pin for RC522*/
#define LED_G   27   /*Pin 8 for LED*/
#define LED_R   12
#define LED_Y   14
#define BUTTON_PIN 34

MFRC522 mfrc522(SS_PIN, RST_PIN);   /*Create MFRC522 initialized*/

void setup()
{
  Serial.begin(115200);   /*Serial Communication begin*/
  SPI.begin();          /*SPI communication initialized*/
  mfrc522.PCD_Init();   /*RFID sensor initialized*/
  pinMode(LED_G, OUTPUT);  /*LED Pin set as output*/
  pinMode(LED_R, OUTPUT);  /*LED Pin set as output*/
  pinMode(LED_Y, OUTPUT);  /*LED Pin set as output*/
  pinMode(BUTTON_PIN, INPUT);
  Serial.println("Put your card to the reader...");
  Serial.println();

}
void loop()
{
  if (digitalRead(BUTTON_PIN)==LOW) {
    digitalWrite(LED_Y, HIGH);
  } else  {
    digitalWrite(LED_Y,LOW);
  }
  /*Look for the RFID Card*/
  if ( ! mfrc522.PICC_IsNewCardPresent())
  {
    return;
  }
  /*Select Card*/
  if ( ! mfrc522.PICC_ReadCardSerial())
  {
    return;
  }
  /*Show UID for Card/Tag on serial monitor*/
  Serial.print("UID tag :");
  String content= "";
  byte letter;
  content.concat("0x");
  for (byte i = 0; i < mfrc522.uid.size; i++)
  {
     //Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
     //Serial.print(mfrc522.uid.uidByte[i]);
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
     int test = content.toInt();
     
  }
  Serial.print(content);
  Serial.println();

  String asciified = "";
  for (int i = 0; i < content.length(); i += 2) {
    char val = content[i] > 0x39 ? (content[i] - 'A') * 16 : (content[i] - '0') * 16;
    val += content[i+1] > 0x39 ? (content[i+1] - 'A') : (content[i+1] - '0');
    Serial.print(val);
    asciified += val; 
  }

  Serial.println("Asciified: ");
  Serial.println(asciified);

  /*
  int array[10];
  String temp = "0x";
  int ctr = 0;
  for (int x = 2; x < content.length(); x++){
    if(x % 2 == 0){
      array[ctr] = temp.toInt();
      temp = "0x";
      ctr += 1 ;
    }
    temp.concat(content[x]);
  }

  Serial.println("Array contents: ");
  for (int z = 0; z < 4; z++){
    Serial.print(array[z]);
  }
  */

  Serial.print("Message : ");
  content.toUpperCase();
  if (content.substring(1) == "03 8F D0 A6") /*UID for the Card/Tag we want to give access Replace with your card UID*/
  {
    Serial.println("Authorized access");  /*Print message if UID match with the database*/
    Serial.println();
    delay(500);
    digitalWrite(LED_G, HIGH);  /*Led Turn ON*/
    delay(2500);
    digitalWrite(LED_G, LOW);
  }
 else   {
    
    Serial.println(" Access denied"); /*If UID do not match print message*/
    digitalWrite(LED_R, HIGH);  /*Led Turn ON*/
    delay(2500);
    digitalWrite(LED_R, LOW);
  }
}