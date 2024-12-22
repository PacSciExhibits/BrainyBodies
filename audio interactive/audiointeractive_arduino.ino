// BRAINY BODIES AUDIO INTERACTIVE
// Oliver Norred, 2024
// olivernorred@gmail.com

#include <Adafruit_NeoPixel.h>
#include <Encoder.h>

#define NUM_PIXELS 16      // Number of LEDs in the ring
#define DELAY_TIME 10    
#define NUM_COLORS 12

#define BUTTON_PIN A0

const long maxDetent = 24; // Controls how fast the encoder reaches max volume
const long midDetent = maxDetent/2;

// NeoPixel rings are connected to pins 10, 11, 12, and 13 (from left to right on the interactive)
Adafruit_NeoPixel rings[] = 
{
  Adafruit_NeoPixel(NUM_PIXELS, 10, NEO_RGBW + NEO_KHZ800),
  Adafruit_NeoPixel(NUM_PIXELS, 11, NEO_RGBW + NEO_KHZ800),
  Adafruit_NeoPixel(NUM_PIXELS, 12, NEO_RGBW + NEO_KHZ800),
  Adafruit_NeoPixel(NUM_PIXELS, 13, NEO_RGBW + NEO_KHZ800)
};

// The optical encoders for the knobs require two pin connections
Encoder encoder1(2, 3);
Encoder encoder2(4, 5);
Encoder encoder3(6, 7);
Encoder encoder4(8, 9);

long position1 = -999;
long position2 = -999;
long position3 = -999;
long position4 = -999;

// set volumes to 50%
long volumes[] = {maxDetent/2, maxDetent/2, maxDetent/2, maxDetent/2};

void setup() {
  Serial.begin(115200);
  for(int i=0; i<4; i++){
    rings[i].begin();
    rings[i].show();   // Initialize all pixels to 'off'
  }

  while (!Serial) {
    ; // Wait for the serial port to connect (necessary for native USB devices)
  }
  // initial update in setup()
  updateLEDRings();
  // initialize "Start" button
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  // Reading serial for when testing (there is no data being sent from the pi to the arduino in the final interactive, so this code block should not run).
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    parseVolumes(input);
    // Clear any remaining data from the buffer until newline
    while (Serial.available() && Serial.read() != '\n') {}
    updateLEDRings();
  }

  // This is used in the final interactive
  readEncoders();
}

void updateLEDRings() {
  for(int i=0; i < 4; i++) {
    int inputPixel = ceil(map(volumes[i], 0, maxDetent, 0, 12));
    if (inputPixel >= 0 && inputPixel < NUM_PIXELS) {   // Check if number is within 0-15
      for (int p=0; p <= inputPixel; p++) {
        rings[i].setPixelColor(15-p, rings[i].Color(0, 150, 20, 0));  // Set specified pixel to red (GRB format)
      }
      for (int p=inputPixel; p <= 15; p++) {
        rings[i].setPixelColor(15-p, rings[i].Color(0, 0, 0, 0));  // Set specified pixel to 0ff
      }
      rings[i].show();                          // Display the updated pixels
    }
  }
}

// Function to parse and set volumes from serial input 
// (this code block should not run in the final interactive because the pi does not send data to the arduino, but it was useful for testing)
void parseVolumes(String input) {
  int idx = 0;
  int start = 0;
  for (int i = 0; i < 4; i++) {
    idx = input.indexOf(',', start);
    if (idx == -1) idx = input.length();  // If no comma, take the rest of the string
    volumes[i] = input.substring(start, idx).toFloat();
    start = idx + 1;
  }
}

// This method does pretty much everything, including calling updateLEDRings()
void readEncoders() {
  // Read the current position of each encoder (initializes at 0)
  // .read() is a method of the Encoder library.
  long newPosition1 = encoder1.read();
  long newPosition2 = encoder2.read();
  long newPosition3 = encoder3.read();
  long newPosition4 = encoder4.read();

  // Constrain all positions between -midDetent and +midDetent (because the volume starts at 50%, so from the start it should be allowed to go up half of the max value or down half of the max value)
  if (newPosition1 < -midDetent) { newPosition1 = -midDetent; encoder1.write(-midDetent); }
  if (newPosition1 >  midDetent) { newPosition1 =  midDetent; encoder1.write( midDetent); }

  if (newPosition2 < -midDetent) { newPosition2 = -midDetent; encoder2.write(-midDetent); }
  if (newPosition2 >  midDetent) { newPosition2 =  midDetent; encoder2.write( midDetent); }

  if (newPosition3 < -midDetent) { newPosition3 = -midDetent; encoder3.write(-midDetent); }
  if (newPosition3 >  midDetent) { newPosition3 =  midDetent; encoder3.write( midDetent); }

  if (newPosition4 < -midDetent) { newPosition4 = -midDetent; encoder4.write(-midDetent); }
  if (newPosition4 >  midDetent) { newPosition4 =  midDetent; encoder4.write( midDetent); }

  // Check if any encoder position has changed
  if (newPosition1 != position1 || newPosition2 != position2 ||
      newPosition3 != position3 || newPosition4 != position4) {
    
    // Set volumes to position vals (range 0 to maxDetent)
    volumes[0] = map(newPosition1, -midDetent, midDetent, 0, maxDetent);
    volumes[1] = map(newPosition2, -midDetent, midDetent, 0, maxDetent);
    volumes[2] = map(newPosition3, -midDetent, midDetent, 0, maxDetent);
    volumes[3] = map(newPosition4, -midDetent, midDetent, 0, maxDetent);

    updateLEDRings();

    // Print the positions in the format "50,50,50,50" (or whatever it is in range 0 to 100)
    // This may be a point of confusion when testing, because the serial message sends an encoder value of `0` as `50`
    // That is to say, the python script on the raspberry pi reads 50 when the arduino reads an encoder value of 0.
    Serial.print(map(newPosition1, -midDetent, midDetent, 0, 100));
    Serial.print(",");
    Serial.print(map(newPosition2, -midDetent, midDetent, 0, 100));
    Serial.print(",");
    Serial.print(map(newPosition3, -midDetent, midDetent, 0, 100));
    Serial.print(",");
    Serial.println(map(newPosition4, -midDetent, midDetent, 0, 100));

    // Update the stored positions
    position1 = newPosition1;
    position2 = newPosition2;
    position3 = newPosition3;
    position4 = newPosition4;
  }

  // Reset all encoder positions to zero (their starting position, half-volume) if a character is received via Serial
  // OR if the button is pressed
  if (Serial.available() || digitalRead(BUTTON_PIN) == LOW) {
    Serial.read();
    encoder1.write(0);
    encoder2.write(0);
    encoder3.write(0);
    encoder4.write(0);
  }
}
