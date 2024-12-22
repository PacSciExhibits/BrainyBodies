// BRAINY BODIES AUDIO INTERACTIVE
// Oliver Norred, 2024
// olivernorred@gmail.com


// Pin definitions
const int switchPin1 = 5;
const int switchPin2 = 6;

// Debounce parameters
const unsigned long debounceDelay = 20; // milliseconds

// initialize switch states (HIGH means not pressed, LOW means pressed)
int switchState1 = HIGH;
int switchState2 = HIGH;
int lastSwitchState1 = HIGH;
int lastSwitchState2 = HIGH;

// Timestamps for debounce timing
unsigned long lastDebounceTime1 = 0;
unsigned long lastDebounceTime2 = 0;

void setup() {
  // Initialize Serial communication
  Serial.begin(9600);

  // Set pins as inputs (using internal pull-up resistors)
  pinMode(switchPin1, INPUT_PULLUP);
  pinMode(switchPin2, INPUT_PULLUP);
}

// This program sends a message via serial to the raspberry pi every time either switch is pressed, in the following format:

// switch1:1
// ^ in the above example message, it indicates that switch1, the switch connected to digital pin 5, has just been pressed (1)

// switch2:0
// ^ in this example message, it indicates that switch2, the switch connected to digital pin 6, has just been released (0)

void loop() {
  // Read the current state of each switch
  int reading1 = digitalRead(switchPin1);
  int reading2 = digitalRead(switchPin2);

  // Debounce for switch 1
  if (reading1 != lastSwitchState1) {
    lastDebounceTime1 = millis(); // Reset the debounce timer
  }
  if ((millis() - lastDebounceTime1) > debounceDelay) {
    // If the reading is stable for debounceDelay, update the state
    if (reading1 != switchState1) {
      switchState1 = reading1;
      // Print the new state only if it changed
      Serial.print("switch1:");
      Serial.println(switchState1 == LOW ? 1 : 0);
    }
  }
  lastSwitchState1 = reading1; // Save the last state for the next loop

  // Debounce for switch 2
  if (reading2 != lastSwitchState2) {
    lastDebounceTime2 = millis(); // Reset the debounce timer
  }
  if ((millis() - lastDebounceTime2) > debounceDelay) {
    // If the reading is stable for debounceDelay, update the state
    if (reading2 != switchState2) {
      switchState2 = reading2;
      // Print the new state only if it changed
      Serial.print("switch2:");
      Serial.println(switchState2 == LOW ? 1 : 0);
    }
  }
  lastSwitchState2 = reading2; // Save the last state for the next loop
}
