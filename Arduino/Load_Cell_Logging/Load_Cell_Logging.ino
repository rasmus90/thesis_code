/***********************************************
   Title:   SD Card and Feather
   Author:  Rasmus Nes Tjoerstad and Jean Raubalt
   Date:    31.01
   Info:    Write data to SD Card
            Added EPPROM stuff and milliseconds
            Stopp writing when signal from Feather
            is received.
            Load cell attached.

 ***********************************************/

char received_char;

// Remaning libraries for SD card, etc.
#include <SD.h>
#include <SoftwareSerial.h>
#include <EEPROM.h>

String load_cell_reading;

// time between readings in ms, ie 20 ms is 50 Hz, ie 10ms is 100Hz
// Now: 10 Hz
#define time_between_readings 1000
// variables for reading intervals
unsigned long last_reading = 0;
unsigned long current_time = 0;
unsigned long start_reading = 0;

const int sensorPin = A3;

int read_feather = 0;
int counter = 0;

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

  if (not(EEPROM_ready == 1)) {
    // initialize
    EEPROM.write(address_init, 1);
    EEPROMWritelong(address_numberReset, 0);
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
  Serial.println(F("Booting"));
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

  // UpdateCurrentFile();

  last_reading = micros();
}


void loop() {

  delayMicroseconds(5);

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

      last_reading = micros();

      load_cell_reading += String(micros());
      load_cell_reading += ",";
    }
  }

  if (is_logging == 1) {

    // chekc if time to do a new reading
    current_time = micros();
    if (current_time - last_reading > time_between_readings) {

      // update current time
      last_reading += time_between_readings;

      // add microsecond information

      // measure
#if SERIAL_PRINT
      time_1 = millis();
#endif

#if SERIAL_PRINT
      time_2 = millis();
#endif


      load_cell_reading += String(analogRead(sensorPin));
      load_cell_reading += ",";

      counter += 1;

#if SERIAL_PRINT
      time_3 = millis();
      Serial.print(F("time change channel: "));
      Serial.println(time_2 - time_1);
      Serial.print(F("time conversion: "));
      Serial.println(time_3 - time_2);
#endif

      //Serial.print("Value: ");
      //Serial.println(load_cell_reading);

      if (counter == 50) {
        load_cell_reading += String(micros());
        load_cell_reading += ",";
      
        // SD post
        postSD(load_cell_reading);

        read_feather = analogRead(pinFeather);

        if (read_feather < 250) {
#if SERIAL_PRINT
          Serial.println(F("stop logging"));
#endif

          postSD("stop loggifeather");

          is_logging = 0;
          UpdateCurrentFile();
        }

        load_cell_reading = "";
        counter = 0;

        load_cell_reading += String(micros());
        load_cell_reading += ",";
      }
    }

  }
}

// function to log a string on the SD card -----------------------------------------------------
void postSD(String load_cell_reading) {

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
    dataFile.println(load_cell_reading);
    // delay(10);
    delayMicroseconds(10);
#if SERIAL_PRINT
    Serial.println("post success");
    // print to the serial port too:
    Serial.println(load_cell_reading);
#endif
  }
  // if the file isn't open, pop up an error:
  // and reboot
  else {
#if SERIAL_PRINT
    Serial.println("post failure");
#endif
    while (1) {
      // do nothing watchdog fires
    }
  }

#if SERIAL_PRINT
  unsigned long endLog = millis();
  Serial.print("Time log end: ");
  Serial.println(endLog);
  Serial.print("Time log delay: ");
  Serial.println(endLog - startLog);
#endif

}

// this function determines what should be the name of the next file
// on which to write and updates the EEPROM
void UpdateCurrentFile() {

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
  EEPROMWritelong(address_numberReset, new_value_fileIndex);

  // generate the string to put as the file numbering
  String str_index = String(new_value_fileIndex);
  int str_length = str_index.length();

  // put the characters of the name at the right place
  for (int ind_rank = 0; ind_rank < str_length; ind_rank++) {
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

