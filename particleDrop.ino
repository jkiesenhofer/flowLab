#include <Stepper.h>

const int stepsPerRevolution = 2048;  // 28BYJ-48

Stepper myStepper(stepsPerRevolution, 9, 11, 10, 12);

void setup() {
  myStepper.setSpeed(10); // RPM
}

void loop() {
  myStepper.step(stepsPerRevolution);  // eine Umdrehung vorwärts
  delay(1000);

  myStepper.step(-stepsPerRevolution); // zurück
  delay(1000);
}
