// For COM5

// Assign button pins
const int BUTTON_PIN1 = 14;
const int BUTTON_PIN2 = 15;
const int BUTTON_PIN3 = 16;

// Initialize timing variables
unsigned long buttonTime1 = millis();
unsigned long buttonTime2 = millis();
unsigned long buttonTime3 = millis();
unsigned long ledTime = millis();
unsigned long motorTime = millis();

void setup() {
  // Set up Bluetooth, OLED, and buzzer motor
  setupCommunication();
  setupDisplay();
  setupMotor();
  // Set up buttons as inputs
  pinMode(BUTTON_PIN1, INPUT);
  pinMode(BUTTON_PIN2, INPUT);
  pinMode(BUTTON_PIN3, INPUT);
  // Set up built-in LED for testing
  pinMode(LED_BUILTIN, OUTPUT);
  // Clear the display
  writeDisplay("", 0, true);
}

void loop() {
  // Update time and message
  unsigned long currentTime = millis();
  String message = receiveMessage();

  // Display message on OLED
  if (message != "") {
    writeDisplay(message.c_str(), 1, true);
  }

  // Turn on buzzer motor if an unfamiliar face appears
  if (message == "UNKNOWN") {
    motorTime = currentTime;
    activateMotor(127);
  }

  // Turn off the motor after 1 second of the stranger leaving the frame
  if (currentTime - motorTime > 1000) {
    deactivateMotor();
  }

  // Detect button press, turn on LED, and send "UNLOCK" to Python
  if (digitalRead(BUTTON_PIN1) == LOW && currentTime - buttonTime1 > 300) {
    buttonTime1 = currentTime;
    ledTime = currentTime;
    digitalWrite(LED_BUILTIN, HIGH);
    sendMessage("UNLOCK");
  }

  // Detect button press, turn on LED, and send "SAVE" to Python
  if (digitalRead(BUTTON_PIN2) == LOW && currentTime - buttonTime2 > 300) {
    buttonTime2 = currentTime;
    ledTime = currentTime;
    digitalWrite(LED_BUILTIN, HIGH);
    sendMessage("SAVE");
  }

  // Detect button press, turn on LED, and send "DISABLE" to Python
  if (digitalRead(BUTTON_PIN3) == LOW && currentTime - buttonTime3 > 300) {
    buttonTime3 = currentTime;
    ledTime = currentTime;
    digitalWrite(LED_BUILTIN, HIGH);
    sendMessage("DISABLE");
  }
  
  // Turn off LED after 300 ms
  if (currentTime - ledTime > 300) {
    digitalWrite(LED_BUILTIN, LOW);
  }
}
