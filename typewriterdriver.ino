

#define DCMOTOR 19
#define PRINTHEAD 20
// pin for sensor on the typewriter which is continuous when the print head reaches a margin
#define INDEX_IN 21
// driver controlling the daisy wheel
//#define WHEEL_STEP D0
//#define WHEEL_DIR B7
// this is for driver #1
#define WHEEL_STEP 5
#define WHEEL_DIR 4
#define WHEEL_DELAY 3000
// driver controlling the paper feed (up-down)
// this is for driver #2
#define FEED_STEP 3
#define FEED_DIR 2
#define FEED_DELAY 3000
// driver controlling the carriage (left-right)
// this is for driver #3
#define CAR_STEP 1
#define CAR_DIR 0
#define CAR_DELAY 3000

int wheel=0;
int car=0;
int feed=0;
unsigned int stepsize=1;

void strike() {
  digitalWrite(PRINTHEAD, HIGH);
  delay(5);
  digitalWrite(PRINTHEAD, LOW);
  digitalWrite(DCMOTOR, HIGH);
  delay(50);
  digitalWrite(DCMOTOR, LOW);
}

int stepTo(int steppin, int dirpin, int del, int current, int steps) {
//  if(current+steps < 0) {
//    Serial.println("tried to step past zero");
//    return current;
//  }
  unsigned int dir;
  if(steps < 0) {
    dir=LOW;
  } else {
    dir=HIGH;
  }
  digitalWrite(dirpin, dir);
  for(int i=0; i<abs(steps); i++) {
    digitalWrite(steppin, HIGH);
    delayMicroseconds(del);
    digitalWrite(steppin, LOW);
    delayMicroseconds(del);
  }
  return current+steps;
}

void resetme() {
  unsigned int resetSteps=0;
  for(int i=0; i<10000; i++) {
    if(digitalRead(INDEX_IN) == LOW) {
      Serial.print(resetSteps);
      Serial.println(" steps to reset");
      break;
    } else {
      stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, 1, -1);
      resetSteps++;
    }
  }

  stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, 1, -6);
  stepTo(WHEEL_STEP, WHEEL_DIR, WHEEL_DELAY, 1, -96*3);
  stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, 1, 50);
  stepTo(WHEEL_STEP, WHEEL_DIR, WHEEL_DELAY, 1, 4);
  stepTo(WHEEL_STEP, WHEEL_DIR, WHEEL_DELAY, 1, -4);
  digitalWrite(WHEEL_DIR, LOW);
  digitalWrite(CAR_DIR, LOW);
  car=0;
  wheel=0;
  feed=0;
}

void setup()
{
  car=0;
  wheel=0;
  feed=0;
  pinMode(DCMOTOR, OUTPUT);
  digitalWrite(DCMOTOR, LOW);
  pinMode(PRINTHEAD, OUTPUT);
  digitalWrite(PRINTHEAD, LOW);
  pinMode(WHEEL_DIR, OUTPUT);
  digitalWrite(WHEEL_DIR, LOW);
  pinMode(WHEEL_STEP, OUTPUT);
  digitalWrite(WHEEL_STEP, LOW);
  pinMode(CAR_DIR, OUTPUT);
  digitalWrite(CAR_DIR, LOW);
  pinMode(CAR_STEP, OUTPUT);
  digitalWrite(CAR_STEP, LOW);
  pinMode(FEED_DIR, OUTPUT);
  digitalWrite(FEED_DIR, LOW);
  pinMode(FEED_STEP, OUTPUT);
  digitalWrite(FEED_STEP, LOW);
  // pull the index pin high
  pinMode(INDEX_IN, INPUT_PULLUP);
  digitalWrite(INDEX_IN, HIGH);
  Serial.begin(9600);
//  resetme();
}

signed int b;
void loop()
{
  b=Serial.read();
  if(b != -1) {
    switch(b) {
      case 'h':
        car=stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, car, -stepsize);
        break;
      case 'l': 
        car=stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, car, stepsize);
        break;
      case 'j':
        feed=stepTo(FEED_STEP, FEED_DIR, FEED_DELAY, feed, -stepsize);
        break;
      case 'k':
        feed=stepTo(FEED_STEP, FEED_DIR, FEED_DELAY, feed, stepsize);
        break;
      case '[':
        wheel=stepTo(WHEEL_STEP, WHEEL_DIR, WHEEL_DELAY, wheel, -stepsize);
        break;
      case ']':
        wheel=stepTo(WHEEL_STEP, WHEEL_DIR, WHEEL_DELAY, wheel, stepsize);
        break;
      case '1':
        stepsize=1;
        break;
      case '2':
        stepsize=10;
        break;
      case '3':
        stepsize=100;
        break;
      case '4':
        stepsize=1000;
        break;
      case '5':
        stepsize+=1;
        break;
      case '6':
        stepsize+=10;
        break;
      case '7':
        stepsize+=100;
        break;
      case '8':
        stepsize+=1000;
        break;
      case '0':
        stepsize=1;
        break;
      case 'r':
        resetme();
        stepsize=1;
        break;
      case 's':
        strike();
        break;
    }
    Serial.print("step size ");
    Serial.print(stepsize);
    Serial.print(" wheel pos ");
    Serial.print(wheel);
    Serial.print(" car pos ");
    Serial.print(car);
    Serial.print(" feed pos ");
    Serial.print(feed);
    Serial.println();
    /*    Serial.print(b);
    if(b >= 32 && b <= 126) {
      spin_to(b);
      strike();
    }
    */
  }
  /*
  digitalWrite(dirpin, LOW);     // Set the direction.
  delay(2000);
  boolean led=false;
  int ledpin=11;  
  for (i = 0; i<200; i++)       // Iterate for 4000 microsteps.
  {
    led=!led;
    digitalWrite(ledpin, led);

    digitalWrite(steppin, LOW);  // This LOW to HIGH change is what creates the
    digitalWrite(steppin, HIGH); // "Rising Edge" so the easydriver knows to when to step.
    delayMicroseconds(400);      // This delay time is close to top speed for this
  }                              // particular motor. Any faster the motor stalls.
*/
}
