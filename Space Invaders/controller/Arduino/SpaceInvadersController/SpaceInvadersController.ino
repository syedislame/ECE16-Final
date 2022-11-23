/*
 * Global variables
 */
// Acceleration values recorded from the readAccelSensor() function
int ax = 0; int ay = 0; int az = 0;
int ppg = 0;        // PPG from readPhotoSensor() (in Photodetector tab)
int sampleTime = 0; // Time of last sample (in Sampling tab)
bool sending;
int status = 0;     // Total lives minus how many lives are remaining
int buzzer = 0;     // 0 = buzzer motor off, 1 = buzzer motor on

// Initialize timing variables to time since program started
unsigned long buttonTime1 = millis();
unsigned long buttonTime2 = millis();
unsigned long motorTime = millis();

// Attach BUTTON_PINs to pins 14 and 15 of the board
const int BUTTON_PIN1 = 14;
const int BUTTON_PIN2 = 15;

/*
 * Initialize the various components of the wearable
 */
void setup() {
  // Set up hardware and communication
  setupAccelSensor();
  setupCommunication();
  setupDisplay();
  setupMotor();
  // Set BUTTON_PINs as inputs
  pinMode(BUTTON_PIN1, INPUT);
  pinMode(BUTTON_PIN2, INPUT);
  sending = false;

` // Write boot messages to display
  writeDisplay("Ready...", 1, true);
  writeDisplay("Set...", 2, false);
  writeDisplay("Play!", 3, false);
}

/*
 * The main processing loop
 */
void loop() {
  // Update currentTime variables to time since beginning of program
  unsigned long currentTime1 = millis();
  unsigned long currentTime2 = millis();

  // Detect for shoot button press and send to Python if pressed
  if (digitalRead(BUTTON_PIN1) == LOW && (currentTime2 - buttonTime1 > 100)) {
    sendMessage("FIRE");
    buttonTime1 = currentTime2;
  }

  // Detect for quit button press and send to Python if pressed
  if (digitalRead(BUTTON_PIN2) == LOW && (currentTime2 - buttonTime2 > 250)) {
    sendMessage("QUIT");
    buttonTime2 = currentTime2;
  }

  String command = receiveMessage();  // receive incoming data from serial buffer

  // Determine the score and how many lives are left
  if (command != "") {  // if the command is not empty
    char commandStart = command[0]; // get the first character of the command
    if (command[0] == 'S') {  // if the first letter of the command is 'S' (for "Score...")
      // Parse the score and life data into two separate strings
      int split = command.indexOf(',');
      String score = command.substring(0,split);
      String lives = command.substring(split+1);

      // Display score and remaining lives on the OLED
      writeDisplay(score.c_str(), 1, true);
      writeDisplay(lives.c_str(), 2, true);

      // Activate motor if a life is lost
      if (lives == "Lives: 3"){
        status = 0;
      }
      else if (lives == "Lives: 2" && status == 0) {
        if (buzzer == 0) {
          activateMotor(120);
          motorTime = currentTime1;
          buzzer = 1;
        }
      }
      else if (lives == "Lives: 1" && status == 1) {
        if (buzzer == 0) {
          activateMotor(120);
          motorTime = currentTime1;
          buzzer = 1;
        }
      }
      else if (lives == "Lives: 0" && status == 2) {
        if (buzzer == 0) {
          activateMotor(120);
          motorTime = currentTime1;
          buzzer = 1;
        }
      }
      else if (lives == "game over" && status == 3) {
        if (buzzer == 0) {
          activateMotor(120);
          motorTime = currentTime1;
          buzzer = 1;
        }
      }
    }
  }
  // Turn off the buzzer motor after one second
  if (currentTime1 - motorTime > 1000 && buzzer == 1){
    status++; // update status to next status
    if (status > 3) status = 0; // cycle status back to 0 if it goes past the last status (3)
    deactivateMotor();  // turn off the motor
    buzzer = 0;
  }

  // Parse command coming from Python (either "stop" or "start")
  if(command == "stop") {
    sending = false;
    writeDisplay("Controller: Off", 0, true);
  }
  else if(command == "start") {
    sending = true;
    writeDisplay("Controller: On", 0, true);
  }

  // Send the sample time and acceleration data
  if(sending && sampleSensors()) {
    String response = String(sampleTime) + ",";
    response += String(ax) + "," + String(ay) + "," + String(az);
    sendMessage(response);
  }
}
