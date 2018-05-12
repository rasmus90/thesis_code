/******************************
 * Title:   Feather Transmit
 * Autor:   Jean/RNT
 * Info:    Include this code
 *          in the MegaMoto_
 *          LightSensor script
 * 
 * 
 *****************************/


#include <SPI.h>
#include <RH_RF95.h>

char serial_char;

/* for feather32u4 */
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 7

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 434.0
 
// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

void setup() {
  delay(1000);

  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);
  
  // initialize digital pin 13 as an output.
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);

  // start usb serial
  Serial.begin(9600);
  while(!Serial){
    // wait
  }

  Serial.println("Feather LoRa TX Test!");
 
  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);
 
  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    while (1);
  }
  Serial.println("LoRa radio init OK!");
 
  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);
  
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on
 
  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
  
  delay(100);
  Serial.println("booted");
  Serial.println("Start [S] / End [E]");
}

// the loop function runs over and over again forever
void loop() {
  if (Serial.available() > 0){
    serial_char = Serial.read();

    if (serial_char == 'S'){
      Serial.println("Start");
      digitalWrite(13, HIGH);
      // send packet
      char radiopacket[1] = "S";
      rf95.send((uint8_t *)radiopacket, 1);
      rf95.waitPacketSent();
      Serial.println("Sent");
    }

    if (serial_char == 'E'){
      Serial.println("End");
      digitalWrite(13, LOW);
      // send packet
      char radiopacket[1] = "E";
      rf95.send((uint8_t *)radiopacket, 1);
      rf95.waitPacketSent();
      Serial.println("Sent");
    }
  }
}
