// For COM8

#include <ESP32Servo.h> // for controlling Servo motor with ESP32

Servo myservo;  // create Servo object to control Servo motor
const int SERVO_PIN = 18; // assign pin 18 as the Servo pin

int pos = 0;  // stores Servo position
bool doorOpened = false;  // stores whether door is opened or closed (false = closed)

unsigned long ledTime = millis(); // stores time that LED last turned on
unsigned long servoTime = millis(); // stores time that door was last unlocked

void setup() {
  // Set up Bluetooth
  setupCommunication();
  // Set up built-in LED for testing
  pinMode(LED_BUILTIN, OUTPUT);
	// Allow allocation of all timers
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myservo.setPeriodHertz(50);    // standard 50 hz servo
  myservo.attach(SERVO_PIN, 500, 2400);  // attach Servo motor to SERVO_PIN
}

void loop() {
  // Update time and message
  unsigned long currentTime = millis();
  String message = receiveMessage();

  // Unlock door if receives "UNLOCK"
  if (message == "UNLOCK") {
    servoTime = currentTime;  // update servoTime to current time
    ledTime = currentTime;    // update ledTime to current time
    doorOpened = true;
    digitalWrite(LED_BUILTIN, HIGH);  // turn on the built-in LED
    myservo.write(90);  // rotate the Servo 90 degrees
    sendMessage("DOOR OPENED");
  }

  // Turn off LED after 1 s
  if (currentTime - ledTime > 1000) {
    digitalWrite(LED_BUILTIN, LOW);
  }
  
  // Lock door after 3 s, send "DOOR CLOSED" to Python, and display message
  if (currentTime - servoTime > 3000 && doorOpened) {
    doorOpened = false;
    myservo.write(0);
    delay(100);
    sendMessage("DOOR CLOSED");
  }
}
