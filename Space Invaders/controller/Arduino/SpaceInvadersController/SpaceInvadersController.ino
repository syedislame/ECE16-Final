/*
 * Global variables
 */
// Acceleration values recorded from the readAccelSensor() function
int ax = 0; int ay = 0; int az = 0;
int ppg = 0;        // PPG from readPhotoSensor() (in Photodetector tab)
int sampleTime = 0; // Time of last sample (in Sampling tab)
bool sending;
int status = 0;
int buzzer = 0;

unsigned long currentTime = millis();
unsigned long buttonTime = millis();
unsigned long motorTime = millis();
/*
 * Initialize the various components of the wearable
 */
void setup() {
  setupAccelSensor();
  setupCommunication();
  setupDisplay();
  setupMotor();
  //setupPhotoSensor();
  sending = false;

  writeDisplay("Ready...", 1, true);
  writeDisplay("Set...", 2, false);
  writeDisplay("Play!", 3, false);
}

/*
 * The main processing loop
 */
void loop() {
  // Parse command coming from Python (either "stop" or "start")
  String command = receiveMessage();


  if (command != "") {
    char commandStart = command[0];
    if (command[0] == 'S'){
      currentTime = millis();
      int split = command.indexOf(',');
      String score = command.substring(0,split);
      String lives = command.substring(split+1);
      writeDisplay(score.c_str(), 1, true);
      writeDisplay(lives.c_str(), 2, true);
      if (lives == "Lives: 3"){
        status = 0;
      }
      else if (lives == "Lives: 2" && status == 0){
        if (buzzer == 0){
          activateMotor(120);
          motorTime = currentTime;
          buzzer = 1;
        }
        if (currentTime - motorTime > 1000){
          status = 1;
          deactivateMotor();
          buzzer = 0;
        }
      }
      else if (lives == "Lives: 1" && status == 1){
        if (buzzer == 0){
          activateMotor(120);
          motorTime = currentTime;
          buzzer = 1;
        }
        if (currentTime - motorTime > 1000){
          status = 2;
          deactivateMotor();
          buzzer = 0;
        }
      }
      else if (lives == "Lives: 0" && status == 2){
        if (buzzer == 0){
          activateMotor(120);
          motorTime = currentTime;
          buzzer = 1;
        }
        if (currentTime - motorTime > 1000){
          status = 3;
          deactivateMotor();
          buzzer = 0;
        }
      }
      else if (lives == "game over" && status == 3){
        if (buzzer == 0){
          activateMotor(120);
          motorTime = currentTime;
          buzzer = 1;
        }
        if (currentTime - motorTime > 1000){
          status = 0;
          deactivateMotor();
          buzzer = 0;
        }
      }

    }
  }
  if(command == "stop") {
    sending = false;
    writeDisplay("Controller: Off", 0, true);
  }
  else if(command == "start") {
    sending = true;
    writeDisplay("Controller: On", 0, true);
  }

  // Send the orientation of the board
  if(sending && sampleSensors()) {
    sendMessage(String(getOrientation()));
  }
}
