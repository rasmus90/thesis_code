/***********************************************
 * Title:   SD Card and Feather
 * Author:  Rasmus Nes Tjoerstad and Jean Raubalt
 * Date:    16.11
 * Info:    Write data to SD Card
 *          Added EPPROM stuff and milliseconds
 *          Stopp writing when signal from Feather
 *          is received.
 *          Thermistor attached to slider surface.
 * 
 ***********************************************/

// Two libraries for Feather 32u4
#include <SPI.h>
#include <RH_RF95.h>

char received_char;

// Remaning libraries for SD card, etc.
#include <SD.h>
#include <Wire.h>
#include <Ard2499.h>
#include <SoftwareSerial.h>
#include <EEPROM.h>

Ard2499 ard2499board1;
Ard2499 ard2499board2;
Ard2499 ard2499board3;
Ard2499 ard2499board4;
Ard2499 ard2499board5;
Ard2499 ard2499board6;
Ard2499 ard2499board7;

// Debug mode: better looking serial output
#define DebugMode true

String thermistor_reading;
int read_feather = 0;

// time between readings in ms, ie 20 ms is 50 Hz, ie 10ms is 100Hz
// Now: 10 Hz
#define time_between_readings 100
// variables for reading intervals
unsigned long last_reading = 0;
unsigned long current_time = 0;
unsigned long start_reading = 0;

unsigned long time_1;
unsigned long time_2;
unsigned long time_3;

#define SERIAL_PRINT 0

// global variables -------------------------------
// filename, will be modified based on EEPROM data for saving on several files
char currentFileName[] = "F00000";
int nbrOfZeros = 5; // number of zeros after the letter in the naming convention

int address_init = 0;
int address_numberReset = 1;

// name of the file on which writing in the SD card library type
File dataFile;

// bool indicating if currently logging
int is_logging = 0;

// analog pin on which to read from Feather
#define pinFeather A1

void setup() {
  
  // let the time to open the serial if needed
  delay(1000);

  // EEPROM check %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  
  // check if the EEPROM has been initialized. If not, do it!
  int EEPROM_ready = EEPROM.read(address_init);
  
  if (not(EEPROM_ready==1)){
    // initialize
    EEPROM.write(address_init,1);
    EEPROMWritelong(address_numberReset,0);
  }
  
  // open serial %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  
  #if SERIAL_PRINT
    // Open serial communications and wait for port to open:
    Serial.begin(57600);
    while (!Serial) {
      ; // wait for serial port to connect.
    }
    Serial.println();
    Serial.println();
    Serial.println("Booting");
  #endif

  // setup SD card %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  
  // see if the card is present and can be initialized:
  if (!SD.begin(10)) {
    #if SERIAL_PRINT
      Serial.println("Card failed, or not present");
    #endif
    // blink to indicate failure
      ;
  }
  #if SERIAL_PRINT
    Serial.println("card initialized.");
  #endif
  
  // end of the setup %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  
  #if SERIAL_PRINT
    Serial.println();
    Serial.println("----- End setup -----");
    Serial.println();
  #endif
  
  // update the EEPROM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  // name of the current file on which writting on the SD card
  UpdateCurrentFile();
  postSD("Mess, Booting from beginning!");

  UpdateCurrentFile();
  

  // connect to ARD-LTC2499
  Wire.begin();

  // start lower board (board 1): controls P15
  ard2499board1.begin(ARD2499_ADC_ADDR_ZZZ, ARD2499_EEP_ADDR_ZZ);
  ard2499board1.ltc2499ChangeConfiguration(LTC2499_CONFIG2_60_50HZ_REJ | LTC2499_CONFIG2_SPEED_2X );
  // Initiate first channel: (remove if old setup is used)
   ard2499board1.ltc2499ChangeChannel(LTC2499_CHAN_SINGLE_15P); 

   // start upper board (board 2): controls P14
   ard2499board2.begin(ARD2499_ADC_ADDR_ZZ1, ARD2499_EEP_ADDR_ZZ);
   ard2499board2.ltc2499ChangeConfiguration(LTC2499_CONFIG2_60_50HZ_REJ | LTC2499_CONFIG2_SPEED_2X );
   ard2499board2.ltc2499ChangeChannel(LTC2499_CHAN_SINGLE_14P);
    
   // start upper board (board 3): controls P13
   ard2499board3.begin(ARD2499_ADC_ADDR_Z11, ARD2499_EEP_ADDR_ZZ);
   ard2499board3.ltc2499ChangeConfiguration(LTC2499_CONFIG2_60_50HZ_REJ | LTC2499_CONFIG2_SPEED_2X );
   ard2499board3.ltc2499ChangeChannel(LTC2499_CHAN_SINGLE_13P);

   // start upper board (board 4): controls P12
   ard2499board4.begin(ARD2499_ADC_ADDR_111, ARD2499_EEP_ADDR_ZZ);
   ard2499board4.ltc2499ChangeConfiguration(LTC2499_CONFIG2_60_50HZ_REJ | LTC2499_CONFIG2_SPEED_2X );
   ard2499board4.ltc2499ChangeChannel(LTC2499_CHAN_SINGLE_12P);

   // start upper board (board 5): controls P11
   ard2499board5.begin(ARD2499_ADC_ADDR_110, ARD2499_EEP_ADDR_ZZ);
   ard2499board5.ltc2499ChangeConfiguration(LTC2499_CONFIG2_60_50HZ_REJ | LTC2499_CONFIG2_SPEED_2X );
   ard2499board5.ltc2499ChangeChannel(LTC2499_CHAN_SINGLE_11P);

   // start upper board (board 6): controls P10
   ard2499board6.begin(ARD2499_ADC_ADDR_100, ARD2499_EEP_ADDR_ZZ);
   ard2499board6.ltc2499ChangeConfiguration(LTC2499_CONFIG2_60_50HZ_REJ | LTC2499_CONFIG2_SPEED_2X );
   ard2499board6.ltc2499ChangeChannel(LTC2499_CHAN_SINGLE_10P);

    // start upper board (board 7): controls P9
   ard2499board7.begin(ARD2499_ADC_ADDR_000, ARD2499_EEP_ADDR_ZZ);
   ard2499board7.ltc2499ChangeConfiguration(LTC2499_CONFIG2_60_50HZ_REJ | LTC2499_CONFIG2_SPEED_2X );
   ard2499board7.ltc2499ChangeChannel(LTC2499_CHAN_SINGLE_9P);


   
  last_reading = millis();
  start_reading = millis();

}


void loop() {

  delayMicroseconds(10);

  if (is_logging == 0) {
#if SERIAL_PRINT
    Serial.println(F("not logging"));
#endif

    // read the output from the feather to see if should start logging
    // log if pin feather is on, ie 3.3 V. Let us take half the ADC range as a cut
    read_feather = analogRead(pinFeather);

    if (read_feather > 250) {
#if SERIAL_PRINT
      Serial.println(F("start logging"));
#endif

      is_logging = 1;

      delay(50);

      postSD("Start logging:");
      postSD(String(read_feather));
      postSD(String(is_logging));

      last_reading = millis();

      //thermistor_reading += String(millis());
      //thermistor_reading += ",";
    }
  }
  if (is_logging == 1){

    current_time = millis();



    // chekc if time to do a new reading
    if (current_time-last_reading >= time_between_readings){
      // update current time
      last_reading += time_between_readings;
  
      // add millisecond information
  
      thermistor_reading += String(millis());
      thermistor_reading += ",";
      
      // measure
      #if SERIAL_PRINT
        time_1 = millis();
      #endif
      //ard2499board1.ltc2499ChangeChannel(LTC2499_CHAN_SINGLE_12P);     //(old setup)
      #if SERIAL_PRINT
        time_2 = millis();
      #endif

      thermistor_reading += ard2499board1.ltc2499Read();
      thermistor_reading += ","; 
      thermistor_reading += String(millis());
      thermistor_reading += ",";

      thermistor_reading += ard2499board2.ltc2499Read();
      thermistor_reading += ",";
      thermistor_reading += String(millis());
      thermistor_reading += ",";
      
      thermistor_reading += ard2499board3.ltc2499Read();
      thermistor_reading += ",";
      thermistor_reading += String(millis());
      thermistor_reading += ",";

      thermistor_reading += ard2499board4.ltc2499Read();
      thermistor_reading += ",";
      thermistor_reading += String(millis());
      thermistor_reading += ",";
      
      thermistor_reading += ard2499board5.ltc2499Read();
      thermistor_reading += ",";
      thermistor_reading += String(millis());
      thermistor_reading += ",";

      thermistor_reading += ard2499board6.ltc2499Read();
      thermistor_reading += ",";
      thermistor_reading += String(millis());
      thermistor_reading += ",";
      

      thermistor_reading += ard2499board7.ltc2499Read();
      thermistor_reading += ",";
      thermistor_reading += String(millis());

      // ReadAndChangeChannel(....) if using several pins on same shield/board.


      #if SERIAL_PRINT
        time_3 = millis();
        Serial.print(F("time change channel: "));
        Serial.println(time_2 - time_1);
        Serial.print(F("time conversion: "));
        Serial.println(time_3 - time_2);
      #endif
      
      Serial.print("Value: ");
      Serial.println(thermistor_reading);
      
  
      // SD post
      postSD(thermistor_reading);
      
      read_feather = analogRead(pinFeather);

      if (read_feather < 250) {
          #if SERIAL_PRINT
          Serial.println(F("stop logging"));
          #endif

          postSD("stop loggifeather");

          is_logging = 0;
          UpdateCurrentFile();
        }
  
      thermistor_reading = "";
      
      
    }

  }
}

// function to log a string on the SD card -----------------------------------------------------
void postSD(String thermistor_reading){

  #if SERIAL_PRINT  
    unsigned long startLog = millis();
    Serial.println("Start post...");
    Serial.print("Time log beginning: ");
    Serial.println(startLog);
  #endif
   
  // note: delay are here to avoid conflicts on using the SD card
  // when using it at high frequency

  // if the file is available, write to it:
  if (dataFile) {
    dataFile.println(thermistor_reading);
    // delay(10);
    delayMicroseconds(10);
    #if SERIAL_PRINT
      Serial.println("post success");
      // print to the serial port too:
      Serial.println(thermistor_reading);
    #endif
  }
  // if the file isn't open, pop up an error:
  // and reboot
  else {
    #if SERIAL_PRINT
      Serial.println("post failure");
    #endif
    while(1){
      // do nothing watchdog fires
    }
  }
  
  #if SERIAL_PRINT
    unsigned long endLog = millis();
    Serial.print("Time log end: ");
    Serial.println(endLog);
    Serial.print("Time log delay: ");
    Serial.println(endLog-startLog);
  #endif
  
}

// this function determines what should be the name of the next file
// on which to write and updates the EEPROM
void UpdateCurrentFile(){

  // note: could be problem at initialization in the setup loop, no file opened yet
  // but the library is handling the exception right  
  // close current file
  delay(5);
  dataFile.close();
  delay(5);
  
  // read the current file number in EEPROM
  long value_before_fileIndex = EEPROMReadlong(address_numberReset); 
  
  // update it by increasing by 1. This is the new file number to write on
  long new_value_fileIndex = value_before_fileIndex + 1;
  EEPROMWritelong(address_numberReset,new_value_fileIndex);

  // generate the string to put as the file numbering
  String str_index = String(new_value_fileIndex);
  int str_length = str_index.length();

  // put the characters of the name at the right place  
  for (int ind_rank = 0; ind_rank < str_length; ind_rank++){
    int i_rank = nbrOfZeros + ind_rank - str_length + 1;
    currentFileName[i_rank] = str_index[ind_rank];
  }
  
  #if SERIAL_PRINT
    Serial.print("str_rank: ");
    Serial.println(str_index);
    Serial.print("File name: ");
    Serial.println(currentFileName);
  #endif
  
  delay(5);
  // open the file. only one file can be open at a time,
  dataFile = SD.open(currentFileName, FILE_WRITE);
  delay(5);
}

void EEPROMWritelong(int address, long value)
      {
      //Decomposition from a long to 4 bytes by using bitshift.
      //One = Most significant -> Four = Least significant byte
      byte four = (value & 0xFF);
      byte three = ((value >> 8) & 0xFF);
      byte two = ((value >> 16) & 0xFF);
      byte one = ((value >> 24) & 0xFF);

      //Write the 4 bytes into the eeprom memory.
      EEPROM.write(address, four);
      EEPROM.write(address + 1, three);
      EEPROM.write(address + 2, two);
      EEPROM.write(address + 3, one);
      }

// This function will take and assembly 4 byte of the Eeprom memory
// in order to form a long variable. 
long EEPROMReadlong(long address)
      {
      //Read the 4 bytes from the eeprom memory.
      long four = EEPROM.read(address);
      long three = EEPROM.read(address + 1);
      long two = EEPROM.read(address + 2);
      long one = EEPROM.read(address + 3);

      //Return the recomposed long by using bitshift.
      return ((four << 0) & 0xFF) + ((three << 8) & 0xFFFF) + ((two << 16) & 0xFFFFFF) + ((one << 24) & 0xFFFFFFFF);
      }

