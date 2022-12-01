// setting PWM properties
const int pwmFrequency = 5000;
const int pwmChannel = 0;
const int pwmBitResolution = 8;

// define the GPIO pin
const int MOTOR_PIN = 18;

// configure the PWM output and attach to motor pin
void setupMotor() {
  ledcSetup(pwmChannel, pwmFrequency, pwmBitResolution);
  ledcAttachPin(MOTOR_PIN, pwmChannel);
}

// write to output of analog pin setting duty cycle to motorPower
void activateMotor(int motorPower) {
  ledcWrite(pwmChannel, motorPower);
}

// write to output of analog pin setting duty cycle to 0
void deactivateMotor() {
  ledcWrite(pwmChannel, 0);
}