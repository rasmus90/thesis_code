/**************************************
 * Title:   Field Motor Control
 * Date:    02.03.18
 * Author:  Rasmus NT
 * About:   Script controls engine and|
 *          initiates logging via feather
 *          LoRa signal.
 * Update:  SafetyCheck during acceleration
 *          phase removed.
 *************************************/

#include<Servo.h>

Servo m1;

int velocity = 0;
int midpoint = 1500;
int amp = 0;
int is_running = 3;
int arm = 1500;
String check;
String answer;
#define STEP 5
#define AMP_DOWN_STEP 50
String s;
void setup() {
  Serial.begin(9600);
  m1.attach(6);
  delay(1000);

  // First time lauching script or has it been reset?
  Serial.println("Send M for mid-throttle (1500) or Z for zero (1000)");
  while(true){
    if (Serial.available() > 0){
      char crrt_char = Serial.read();

      if (crrt_char == 'M'){
        Serial.println("Setting throttle to 1500.");
        m1.writeMicroseconds(1500);
        break;
      }
      if (crrt_char == 'Z'){
        Serial.println("Setting throttle to 1000.");
        m1.writeMicroseconds(1000);
        is_running = 0;
        break;
      }
      else{
        Serial.println("Invalid character. Try again.");
      }
    }
  }

  // set motor to midpoint


  // Request speed to amp up too.
  Serial.println("Set speed to amp up to. Value between 1000 and 2000: ");
  while(true){
    while(Serial.available() == 0){
      // pass
    }
  
    velocity = Serial.parseInt();
  
    if ((velocity > 2000) || (velocity < 1000)){
      Serial.println("Invalid value! 1000  to 2000");
      Serial.println("Try again."); 
    }
    else{
      Serial.print("Received ");
      Serial.println(velocity);
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
        Serial.println("Invalid character. Try again.");
      }
    }
  }


  Serial.println("Starting motor.");

}

void(* resetFunc) (void) = 0; //declare reset function @ address 0

void loop() {
  // put your main code here, to run repeatedly:

  if (is_running == 3){
    Serial.println("Arm motor. Transmitting 0 throttle signal.");
    /*
    for (arm = midpoint; arm >= 1000; arm-= AMP_DOWN_STEP){
      m1.writeMicroseconds(arm);
      Serial.println(arm);
      delay(100);
    }
    */
    m1.writeMicroseconds(1000);
    delay(1000);
    is_running = 0;
  }

  // Acceleration phase.
  if (is_running == 0){
    Serial.println("Increasing velocity");
    for (amp = 1000 ; amp < velocity; amp +=STEP){
      m1.writeMicroseconds(amp);  
      delay(198);

    }
    is_running = 1;
    velocity = amp;
    Serial.println(String(amp));
    Serial.println("Finish amping up.");
    delay(10);
    
  }

  // running at constant speed. Turn off or keep running.

  if (is_running == 1){
    Serial.println(String(velocity));
    delay(50);
    check = safetyCheck();
    if (check == "y"){
      Serial.println("Amping down.");
      velocity = ampDown(velocity);
      Serial.print("Velocity after amp down: ");
      Serial.println(String(velocity));
      is_running = 2;
      delay(1000);
      //resetFunc();  //call reset
    }
  }
}

int ampDown(int current_velocity){
  for (velocity = current_velocity; velocity > 1000; velocity -= AMP_DOWN_STEP){
    m1.writeMicroseconds(velocity);
    Serial.println(String(velocity));
    delay(100);
  }
  m1.writeMicroseconds(1000);

  return velocity;
  
}

String safetyCheck(void){
    
    Serial.println("Turn off? y/n");
    while(true){
    while(Serial.available() == 0){
      // pass
    }
    answer = Serial.readString();
    if ((answer == "y" || answer == "n")){
        return answer;  
    }
    else{
      Serial.print("Non-valid answer. Try again.");
    }
  }
}

void softReset(void){
asm volatile ("  jmp 0");
}




