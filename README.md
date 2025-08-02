<img width="3188" height="1202" alt="frame (3)" src="https://github.com/user-attachments/assets/517ad8e9-ad22-457d-9538-a9e62d137cd7" />


# Ai thangappam Robo 🎯


## Basic Details
### Team Name: Ashik M


### Team Members
- Team Lead: Ashik M (individual)

### Project Description
A crazy AI buddy that talks in Malayalam, waves back when you wave, shows emotions on a tiny screen, and even roasts you! It listens, watches your gestures, plays sounds, and reacts like it’s alive. Full of attitude, desi vibes, and total madness

### The Problem (that doesn't exist)
You know how most assistants are just... boring? Too polite, too robotic. We figured, why not make one that actually has personality? One that talks back, roasts you a little, reacts when you wave, and shows emotions—because your tech should have some drama too! 

### The Solution (that nobody asked for)

You know how most assistants are just... boring? Too polite, too robotic. We figured, why not make one that actually has personality? One that talks back, roasts you a little, reacts when you wave, and shows emotions
So, we built an AI buddy that speaks Malayalam, watches you through a webcam, responds to your hand gestures, and shows moods on a tiny face screen. 

## Technical Details
### Technologies/Components Used
For Software:
- [Languages used]:C and python
- [Frameworks used]: arduino
- [Libraries used]:
speech_recognition – For capturing and processing voice commands

playsound – To play fun sound effects

opencv-python – For real-time camera input and gesture detection

mediapipe – To detect hand gestures with accuracy

malayalam-tts – To make it talk back in Malayalam

pyserial – To communicate with the Arduino for emotion display

Adafruit_SSD1306 & Adafruit_GFX (Arduino side) – For OLED display animations
- [Tools used]

For Hardware:
arduino
oled


### Implementation
For Software:python
# Installation
[commands]:# Clone the project (if applicable)
git clone https://github.com/your-repo/malayalam-ai-assistant.git  
cd malayalam-ai-assistant

# Install Python libraries
pip install speechrecognition playsound==1.2.2 opencv-python mediapipe pyserial

# If using Malayalam TTS package
pip install malayalam-tts

# (Optional) Install PyAudio if not already installed
pip install pyaudio  # May require portaudio dependencies on Linux

# Upload Arduino code separately using Arduino IDE with Adafruit libraries:
# - Adafruit_SSD1306
# - Adafruit_GFX


# Run
python filename

### Project Documentation
For Software:python 

# Screenshots (Add at least 3)
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/ed902f96-03a7-479a-bc06-58b8233b0f77" />



For Hardware:

# Schematic & Circuit
<img width="958" height="991" alt="Untitled Sketch 2_bb" src="https://github.com/user-attachments/assets/1123b090-10fa-44a1-8292-8cd4df64af1e" />


oled connected to arduino scl and sda pins and arduino serial communicate to laptop or pi

<img width="1140" height="809" alt="Untitled Sketch 2_schem" src="https://github.com/user-attachments/assets/cb7e5de0-0fad-48ff-bd54-da73afc27515" />


# Build Photos
<img width="1280" height="960" alt="image" src="https://github.com/user-attachments/assets/1b58c167-459f-4028-a1c7-def2c02c180a" />
<img width="960" height="1280" alt="image" src="https://github.com/user-attachments/assets/cc6cca0f-6518-42b8-a7d7-da6b066dbb92" />
<img width="1280" height="960" alt="image" src="https://github.com/user-attachments/assets/0c42cac1-6141-4393-bcd7-2850d712bb13" />

arduino
oled
raspberry pi 

<img width="1280" height="960" alt="image" src="https://github.com/user-attachments/assets/eb3c660d-37d1-426a-b435-0ee901765616" />

Set up the Arduino OLED face

Connect an OLED display (SSD1306) to an Arduino.

Upload code that receives serial data and changes expressions (happy, sad, angry, etc.) on the screen.

Write the Python brain

Create a Python script to:

Listen to your voice using speech_recognition

Process the command and decide what to do (roast, greet, play sound, etc.)

Detect hand gestures using webcam + OpenCV + MediaPipe

Trigger reactions based on gestures (like showing anger when you point a gun sign)

Connect with Arduino

Use pyserial to send emotion commands from Python to Arduino.

For example: if you wave, Python sends happy; if you show a gun sign, it sends angry.

Make it talk back

Use malayalam-tts to generate Malayalam audio responses.

Play sounds using playsound to add funny effects or roasts.

Test the madness

Run your Python script.

Say something like “ഹലോ” or wave at the camera.

<img width="960" height="1280" alt="image" src="https://github.com/user-attachments/assets/ed7a8fe3-e4b3-407e-a92b-79bf05178d1d" />


The final build is a fully working AI assistant that listens, watches, and feels—well, almost!

The Arduino + OLED acts as the face of the assistant, showing real-time emotions like happy, angry, sad, or confused based on what you do or say.

The Python script running on your computer is the brain. It:

Listens to your voice in Malayalam, English, or Tamil

Watches your gestures using the webcam

Thinks about how to react (either roast you, talk, play a sound, or change mood)

Talks back using Malayalam TTS and fun sound effects

Sends commands to the Arduino to show matching facial expressions

If you say "ഹലോ", it greets you back. Show a gun gesture? It gets angry. Wave your hand? It gets happy and playful!

### Project Demo
# Video
https://drive.google.com/file/d/1Y8inVsxCj8FkCi6PpKgC-CABUjGR0Fli/view?usp=drivesdk




---
Made with ❤️ at TinkerHub Useless Projects 

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--25-25?link=https%3A%2F%2Fwww.tinkerhub.org%2Fevents%2FQ2Q1TQKX6Q%2FUseless%2520Projects)



