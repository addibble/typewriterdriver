

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
// microstep pin for wheel
#define WHEEL_MS1 12
#define WHEEL_DELAY 2000
// driver controlling the paper feed (up-down)
// this is for driver #2
#define FEED_STEP 3
#define FEED_DIR 2
// enable pin for feed
#define FEED_EN 11
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
unsigned int resetSteps=0;

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
  digitalWrite(FEED_EN, LOW);
  for(int i=0; i<10000; i++) {
    if(digitalRead(INDEX_IN) == LOW) {
      break;
    } else {
      stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, 1, -1);
      resetSteps++;
    }
  }

  stepTo(WHEEL_STEP, WHEEL_DIR, WHEEL_DELAY, 1, 96*2);
  stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, 1, -40);
  stepTo(WHEEL_STEP, WHEEL_DIR, WHEEL_DELAY, 1, -96*2);
  stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, 1, 24);

  car=0;
  wheel=0;
  feed=0;

  digitalWrite(WHEEL_DIR, LOW);
  digitalWrite(CAR_DIR, LOW);
  digitalWrite(FEED_EN, HIGH);
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
  pinMode(FEED_EN, OUTPUT);
  digitalWrite(FEED_EN, HIGH);
  pinMode(WHEEL_MS1, OUTPUT);
  digitalWrite(WHEEL_MS1, LOW);
  // pull the index pin high
  pinMode(INDEX_IN, INPUT_PULLUP);
  digitalWrite(INDEX_IN, HIGH);

  Serial.begin(115200);
//  resetme();
}

signed int b;
void loop()
{
  b=Serial.read();
  if(b != -1) {
    digitalWrite(FEED_EN, LOW);
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
      case 'q':
        feed=stepTo(FEED_STEP, FEED_DIR, FEED_DELAY, feed, -30);
        for(int i=0; i<50; i++) {    
          wheel=stepTo(WHEEL_STEP, WHEEL_DIR, WHEEL_DELAY, wheel, 2);
          car=stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, car, 12);
          strike();
        }
        car=stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, car, -car);
        feed=stepTo(FEED_STEP, FEED_DIR, FEED_DELAY, feed, -30);
        for(int i=0; i<50; i++) {    
          wheel=stepTo(WHEEL_STEP, WHEEL_DIR, WHEEL_DELAY, wheel, 2);
          car=stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, car, 12);
          strike();
        }
        car=stepTo(CAR_STEP, CAR_DIR, CAR_DELAY, car, -car);
        feed=stepTo(FEED_STEP, FEED_DIR, FEED_DELAY, feed, -60);
        break;
      case 'x':
        Serial.print(stepsize);
        Serial.print(" ");
        Serial.print(wheel);
        Serial.print(" ");
        Serial.print(car);
        Serial.print(" ");
        Serial.print(feed);
        break;
    }
    Serial.println(".");
    digitalWrite(FEED_EN, HIGH);
  }
}
