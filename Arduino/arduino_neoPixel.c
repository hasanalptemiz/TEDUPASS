

#include <Adafruit_NeoPixel.h>

#define PIN 3
int incomingByte;
Adafruit_NeoPixel strip = Adafruit_NeoPixel(16, PIN, NEO_GRB + NEO_KHZ800);

void setup()
{
  Serial.begin(9600);
  strip.begin();
  strip.setBrightness(60); 
  strip.show();          
}

int counter = 0;
void loop()
{

  if (Serial.available() > 0)
  {

    incomingByte = Serial.read();
    if (incomingByte == 'T')
    {
      colorWipe(strip.Color(0, 64, 0), 100); // Green
      delay(3000);
      colorWipe(strip.Color(0, 0, 64), 100); // Blue
    }
    if (incomingByte == 'F')
    {

      colorWipe(strip.Color(64, 0, 0), 100); // Red
      delay(3000);
      colorWipe(strip.Color(0, 0, 64), 100); // Blue
    }
  }
}

void colorWipe(uint32_t c, uint8_t wait)
{
  for (uint16_t i = 0; i < strip.numPixels(); i++)
  {
    strip.setPixelColor(i, c);
    strip.show();
    delay(wait);
  }
}
