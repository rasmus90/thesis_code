/***************************************
Title:    MegaMoto and Light Sensor
Date:     30.10
Author:   Rasmus Nes Tjørstad
Info:     Script to control the MegaMoto
          GT shield and cthe light sensor
          stopping mechanism.

          If light:   engine goes (slowly)
          If dark:    engine stop.
          Frequency:  10 Hz
                      This is adjuset by
                      the delay.

***************************************/
// pins for the control of the Moto shield
// should correspond with the jumpers on the board

// should be able to read raw ADC value and relate it to
// the duty cycle value, e.g. ADCraw = 1023 should correspond
// to duty cycle = 255

// parameters -----------------------------------
// ----------------------------------------------
#define VELOCITY_COUNT 200
#define DEBUG false
// ----------------------------------------------
// end parameters -------------------------------

#define lightSensor A0

int EnablePin = 13;
int duty = 0;
int PWMPin = 11;  // Timer2
int PWMPin2 = 3;

int lightRaw;      // raw A/D value
float lightVal;    // adjusted Amps value

int max_ = 100;
int inc = 2;
int pause = 50;

int value_in = 0;

void setup() {
  Serial.begin(9600);  

  Serial.println();
  Serial.println("Start new experiment");
               
  // disable moto shield so long as not needed
  pinMode(EnablePin, OUTPUT);
  digitalWrite(EnablePin, LOW);  // so that no empty resistance

  // prepare PWM control pins
  pinMode(PWMPin, OUTPUT);    // backwards
  pinMode(PWMPin2, OUTPUT);   // forwards

  // change Timer2 divisor to 1 gives 31.2kHz PWM freq
  setPwmFrequency(PWMPin, 1);
  setPwmFrequency(PWMPin2, 1);

  Serial.println("Give engine value (0 to 255)");

  while(true){
    while(Serial.available() == 0){
      // pass
    }
  
    value_in = Serial.parseInt();
  
    if ((value_in > 255) || (value_in < 0)){
      Serial.println("Invalid value! 0  to 255"); 
    }
    else{
      Serial.print("Received ");
      Serial.println(value_in);
      break;
    }
  }

  Serial.println("Send char S to start, other to reboot");

  while(true){
    if (Serial.available() > 0){
      char crrt_char = Serial.read();

      if (crrt_char == 'S'){
        break;
      }
      else{
        softReset();
      }
    }
  }

  // start motion
  digitalWrite(EnablePin, HIGH);
  analogWrite(PWMPin, 0);
  
}


void loop() {

    #if DEBUG
      Serial.println(lightRaw);
    #endif
    
    if (duty == 0){
        if (lightRaw > 100){
          for (duty = 0; duty <= value_in; duty += 5){
            delay(10);
            analogWrite(PWMPin2, duty);
            check_light_sensor();
            
        }
      }
    }
    
    check_light_sensor();
}
/*
* Divides a given PWM pin frequency by a divisor.
*
* The resulting frequency is equal to the base frequency divided by
* the given divisor:
*   - Base frequencies:
*      o The base frequency for pins 3, 9, 10, and 11 is 31250 Hz.
*      o The base frequency for pins 5 and 6 is 62500 Hz.
*   - Divisors:
*      o The divisors available on pins 5, 6, 9 and 10 are: 1, 8, 64,
*        256, and 1024.
*      o The divisors available on pins 3 and 11 are: 1, 8, 32, 64,
*        128, 256, and 1024.
*
* PWM frequencies are tied together in pairs of pins. If one in a
* pair is changed, the other is also changed to match:
*   - Pins 5 and 6 are paired (Timer0)
*   - Pins 9 and 10 are paired (Timer1)
*   - Pins 3 and 11 are paired (Timer2)
*
* Note that this function will have side effects on anything else
* that uses timers:
*   - Changes on pins 5, 6 may cause the delay() and
*     millis() functions to stop working. Other timing-related
*     functions may also be affected.
*   - Changes on pins 9 or 10 will cause the Servo library to function
*     incorrectly.
*
* Thanks to macegr of the Arduino forums for his documentation of the
* PWM frequency divisors. His post can be viewed at:
*   http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1235060559/0#4
*/

void check_light_sensor(void){
  lightRaw = analogRead(lightSensor);
  
  if (lightRaw < 140){
      analogWrite(PWMPin2, 0);
      Serial.println("Light sensor stop");
      Serial.println("Reboot");
      delay(1000);
     
      softReset();
    }
}

void softReset(void){
asm volatile ("  jmp 0");
}

void setPwmFrequency(int pin, int divisor) {
  byte mode;
  if(pin == 5 || pin == 6 || pin == 9 || pin == 10) { // Timer0 or Timer1
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 64: mode = 0x03; break;
      case 256: mode = 0x04; break;
      case 1024: mode = 0x05; break;
      default: return;
    }
    if(pin == 5 || pin == 6) {
      TCCR0B = TCCR0B & 0b11111000 | mode; // Timer0
    } else {
      TCCR1B = TCCR1B & 0b11111000 | mode; // Timer1
    }
  } else if(pin == 3 || pin == 11) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 32: mode = 0x03; break;
      case 64: mode = 0x04; break;
      case 128: mode = 0x05; break;
      case 256: mode = 0x06; break;
      case 1024: mode = 0x7; break;
      default: return;
    }
    //TCCR2B = TCCR2B & 0b11111000 | mode; // Timer2
  }
}


