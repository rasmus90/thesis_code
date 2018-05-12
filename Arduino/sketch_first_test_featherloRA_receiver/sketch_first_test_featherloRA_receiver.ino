/****************************
 * Title:  Feather Receive
 * Autor:  RNT
 * 
 * 
 **************************/

#include <SPI.h>
#include <RH_RF95.h>

char received_char;

#define SERIAL_PRINT false

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

  #if SERIAL_PRINT
    // start usb serial
    Serial.begin(9600);
    while(!Serial){
      // wait
    }
    Serial.println("Feather LoRa TX Test!");
  #endif
 
  while (!rf95.init()) {
    #if SERIAL_PRINT
    Serial.println("LoRa radio init failed");
    #endif
    while (1);
  }
  
  #if SERIAL_PRINT
  Serial.println("LoRa radio init OK!");
  #endif
 
  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    #if SERIAL_PRINT
    Serial.println("setFrequency failed");
    #endif
    
    while (1);
  }
  
  #if SERIAL_PRINT
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);
  #endif
  
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on
 
  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
  
  delay(100);

  #if SERIAL_PRINT
  Serial.println("booted");
  Serial.println("ready to receive");
  #endif
}

// the loop function runs over and over again forever
void loop() {
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);
 
  if (rf95.waitAvailableTimeout(1))
  { 
    if (rf95.recv(buf, &len))
   {
      received_char = char(buf[0]);

      #if SERIAL_PRINT
      Serial.print("Received ");
      Serial.println(received_char);
      Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);
      #endif

      if (received_char == 'S'){
        digitalWrite(13, HIGH);
      }

      if (received_char == 'E'){
        digitalWrite(13, LOW);
      }
    }
    else
    {
      #if SERIAL_PRINT
      Serial.println("Receive failed");
      #endif
    }
  }
  
}
