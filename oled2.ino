#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET     -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// 👁 Blink Animation
void animateBlink() {
  for (int blink = 0; blink < 3; blink++) {
    // Eyes open - crescent style
    display.clearDisplay();

    // Left eye
    display.fillCircle(40, 32, 18, SSD1306_WHITE);
    display.fillCircle(40, 38, 15, SSD1306_BLACK);

    // Right eye
    display.fillCircle(88, 32, 18, SSD1306_WHITE);
    display.fillCircle(88, 38, 15, SSD1306_BLACK);

    display.display();
    delay(800);

    // Eyes closed - line style
    display.clearDisplay();
    display.drawLine(25, 32, 55, 32, SSD1306_WHITE); // left closed
    display.drawLine(73, 32, 103, 32, SSD1306_WHITE); // right closed

    display.display();
    delay(200);
  }
}

// 👋 Hand Wave Animation
void animateWave() {
  for (int wave = 0; wave < 3; wave++) {
    // Frame 1 - hand up
    display.clearDisplay();

    // Eyes open
    display.fillCircle(40, 32, 18, SSD1306_WHITE);
    display.fillCircle(40, 38, 15, SSD1306_BLACK);
    display.fillCircle(88, 32, 18, SSD1306_WHITE);
    display.fillCircle(88, 38, 15, SSD1306_BLACK);

    // Hand raised
    display.fillCircle(110, 15, 6, SSD1306_WHITE);       // hand
    display.drawLine(100, 25, 110, 15, SSD1306_WHITE);   // arm

    display.display();
    delay(300);

    // Frame 2 - hand down
    display.clearDisplay();

    // Eyes same
    display.fillCircle(40, 32, 18, SSD1306_WHITE);
    display.fillCircle(40, 38, 15, SSD1306_BLACK);
    display.fillCircle(88, 32, 18, SSD1306_WHITE);
    display.fillCircle(88, 38, 15, SSD1306_BLACK);

    // Hand lowered
    display.fillCircle(110, 30, 6, SSD1306_WHITE);       // hand
    display.drawLine(100, 25, 110, 30, SSD1306_WHITE);   // arm

    display.display();
    delay(300);
  }
}


void animateEmoGun() {
  for (int pose = 0; pose < 3; pose++) {
    // Sad/emo eyes with gun pose
    display.clearDisplay();
    
    // Emo eyes - droopy/sad style
    display.fillCircle(35, 25, 12, SSD1306_WHITE);
    display.fillCircle(35, 30, 10, SSD1306_BLACK); // droopy pupil
    display.fillCircle(93, 25, 12, SSD1306_WHITE);
    display.fillCircle(93, 30, 10, SSD1306_BLACK); // droopy pupil
    
    // Sad eyebrows (angled down)
    display.drawLine(25, 15, 40, 20, SSD1306_WHITE);
    display.drawLine(83, 20, 98, 15, SSD1306_WHITE);
    
    // Gun pointed at "head" - simple gun shape
    display.drawLine(110, 15, 125, 15, SSD1306_WHITE); // barrel
    display.fillRect(108, 12, 8, 6, SSD1306_WHITE); // grip
    display.fillRect(105, 16, 6, 4, SSD1306_WHITE); // trigger guard
    
    // Arm holding gun
    display.drawLine(100, 25, 108, 18, SSD1306_WHITE);
    
    // Dramatic text
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(10, 50);
    display.print("why even try...");
    
    display.display();
    delay(1500);
    
    // Shaking/trembling effect
    display.clearDisplay();
    
    // Same elements but slightly offset for shake effect
    display.fillCircle(36, 26, 12, SSD1306_WHITE);
    display.fillCircle(36, 31, 10, SSD1306_BLACK);
    display.fillCircle(92, 24, 12, SSD1306_WHITE);
    display.fillCircle(92, 29, 10, SSD1306_BLACK);
    
    // Shaky eyebrows
    display.drawLine(24, 14, 41, 19, SSD1306_WHITE);
    display.drawLine(82, 19, 99, 14, SSD1306_WHITE);
    
    // Gun slightly shaking
    display.drawLine(109, 14, 124, 14, SSD1306_WHITE);
    display.fillRect(107, 11, 8, 6, SSD1306_WHITE);
    display.fillRect(104, 15, 6, 4, SSD1306_WHITE);
    display.drawLine(99, 24, 107, 17, SSD1306_WHITE);
    
    display.setCursor(15, 52);
    display.print("i can't do it");
    
    display.display();
    delay(800);
    
    // Gun lowered, ultimate sadness
    display.clearDisplay();
    
    // Even sadder eyes - almost closed
    display.drawLine(25, 25, 45, 30, SSD1306_WHITE);
    display.drawLine(83, 30, 103, 25, SSD1306_WHITE);
    
    // Tear drops
    display.fillCircle(48, 35, 2, SSD1306_WHITE);
    display.fillCircle(80, 35, 2, SSD1306_WHITE);
    
    // Gun lowered/dropped
    display.drawLine(115, 35, 125, 35, SSD1306_WHITE);
    display.fillRect(113, 32, 6, 6, SSD1306_WHITE);
    display.fillRect(111, 36, 4, 3, SSD1306_WHITE);
    
    // Drooped arm
    display.drawLine(105, 40, 113, 35, SSD1306_WHITE);
    
    display.setCursor(5, 52);
    display.print("existence is pain");
    
    display.display();
    delay(2000);
  }
  
  // Return to normal sad state
  display.clearDisplay();
  display.fillCircle(35, 25, 12, SSD1306_WHITE);
  display.fillCircle(35, 30, 8, SSD1306_BLACK);
  display.fillCircle(93, 25, 12, SSD1306_WHITE);
  display.fillCircle(93, 30, 8, SSD1306_BLACK);
  display.display();
}
void setup() {
  Serial.begin(9600);

  // OLED Start
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C
    Serial.println(F("SSD1306 failed"));
    for (;;);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 28);
  display.println("OLED Ready ✅");
  display.display();
  delay(1000);
}

void animateBlast() {
  for (int blast = 0; blast < 2; blast++) {
    // Pre-blast - charging up
    display.clearDisplay();
    
    // Eyes glowing/charging
    display.fillCircle(40, 32, 15, SSD1306_WHITE);
    display.fillCircle(88, 32, 15, SSD1306_WHITE);
    
    // Small energy particles around eyes
    display.fillCircle(25, 25, 2, SSD1306_WHITE);
    display.fillCircle(55, 20, 2, SSD1306_WHITE);
    display.fillCircle(75, 25, 2, SSD1306_WHITE);
    display.fillCircle(105, 20, 2, SSD1306_WHITE);
    
    display.display();
    delay(300);
    
    // Blast frame 1 - initial explosion
    display.clearDisplay();
    
    // Bright eye centers
    display.fillCircle(40, 32, 8, SSD1306_WHITE);
    display.fillCircle(88, 32, 8, SSD1306_WHITE);
    
    // Explosion rays from eyes
    display.drawLine(40, 32, 20, 15, SSD1306_WHITE);
    display.drawLine(40, 32, 15, 32, SSD1306_WHITE);
    display.drawLine(40, 32, 20, 50, SSD1306_WHITE);
    display.drawLine(40, 32, 60, 15, SSD1306_WHITE);
    display.drawLine(40, 32, 65, 50, SSD1306_WHITE);
    
    display.drawLine(88, 32, 110, 15, SSD1306_WHITE);
    display.drawLine(88, 32, 115, 32, SSD1306_WHITE);
    display.drawLine(88, 32, 110, 50, SSD1306_WHITE);
    display.drawLine(88, 32, 65, 15, SSD1306_WHITE);
    display.drawLine(88, 32, 65, 50, SSD1306_WHITE);
    
    // Explosion particles
    display.fillCircle(10, 10, 3, SSD1306_WHITE);
    display.fillCircle(118, 10, 3, SSD1306_WHITE);
    display.fillCircle(10, 55, 3, SSD1306_WHITE);
    display.fillCircle(118, 55, 3, SSD1306_WHITE);
    
    display.display();
    delay(200);
    
    // Blast frame 2 - expanding explosion
    display.clearDisplay();
    
    // Larger explosion circles
    display.drawCircle(40, 32, 20, SSD1306_WHITE);
    display.drawCircle(88, 32, 20, SSD1306_WHITE);
    display.drawCircle(64, 32, 35, SSD1306_WHITE);
    
    // More explosion rays
    display.drawLine(64, 32, 5, 5, SSD1306_WHITE);
    display.drawLine(64, 32, 123, 5, SSD1306_WHITE);
    display.drawLine(64, 32, 5, 60, SSD1306_WHITE);
    display.drawLine(64, 32, 123, 60, SSD1306_WHITE);
    display.drawLine(64, 32, 0, 32, SSD1306_WHITE);
    display.drawLine(64, 32, 128, 32, SSD1306_WHITE);
    
    // Flying debris
    display.fillRect(15, 20, 3, 3, SSD1306_WHITE);
    display.fillRect(110, 45, 3, 3, SSD1306_WHITE);
    display.fillRect(30, 55, 2, 2, SSD1306_WHITE);
    display.fillRect(95, 15, 2, 2, SSD1306_WHITE);
    
    display.display();
    delay(200);
    
    // Blast frame 3 - maximum explosion
    display.clearDisplay();
    
    // Fill most of screen with explosion
    display.fillCircle(64, 32, 45, SSD1306_WHITE);
    display.fillCircle(64, 32, 35, SSD1306_BLACK);
    display.fillCircle(64, 32, 25, SSD1306_WHITE);
    display.fillCircle(64, 32, 15, SSD1306_BLACK);
    
    // Explosion text
    display.setTextSize(2);
    display.setTextColor(SSD1306_BLACK);
    display.setCursor(35, 25);
    display.print("BOOM");
    
    display.display();
    delay(400);
    
    // Blast frame 4 - smoke/aftermath
    display.clearDisplay();
    
    // Smoke clouds
    display.drawCircle(30, 25, 8, SSD1306_WHITE);
    display.drawCircle(35, 30, 6, SSD1306_WHITE);
    display.drawCircle(40, 20, 7, SSD1306_WHITE);
    
    display.drawCircle(90, 25, 8, SSD1306_WHITE);
    display.drawCircle(95, 30, 6, SSD1306_WHITE);
    display.drawCircle(85, 20, 7, SSD1306_WHITE);
    
    display.drawCircle(64, 40, 10, SSD1306_WHITE);
    display.drawCircle(64, 50, 8, SSD1306_WHITE);
    
    // Sparks/embers
    display.fillCircle(20, 40, 1, SSD1306_WHITE);
    display.fillCircle(108, 45, 1, SSD1306_WHITE);
    display.fillCircle(50, 55, 1, SSD1306_WHITE);
    display.fillCircle(80, 10, 1, SSD1306_WHITE);
    
    display.display();
    delay(600);
    
    // Clear aftermath
    display.clearDisplay();
    display.display();
    delay(300);
  }
}

void loop() {
   if (Serial.available() > 0) {
    int command = Serial.parseInt();
    
    switch(command) {
      case 1:
        Serial.println("Executing: Blink");
        animateBlink();
        break;
      case 4:
        animateBlast();
        break;
      case 2:
        animateWave();
        break;
      default:
        animateBlink();
        if(command != 0) {
          Serial.println("Invalid command. Use 1-5");
        }
        break;
    }
  while(Serial.available() > 0) {
      Serial.read();
    }
  animateBlink();  // 👁 Blink animation
  delay(1000);


}}
