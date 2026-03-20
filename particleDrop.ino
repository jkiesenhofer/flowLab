// Pin 13 has the built-in LED
const int ledPin = 13;

void setup() {
  // Set LED pin as output
  pinMode(ledPin, OUTPUT);
}

void loop() {
  digitalWrite(ledPin, HIGH); // Turn LED on
  delay(1000);                 // Wait 1 second
  digitalWrite(ledPin, LOW);  // Turn LED off
  delay(1000);                 // Wait 1 second
}
