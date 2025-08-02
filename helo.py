import speech_recognition as sr
import requests
import os
import serial
import time
from malayalam_tts import speak_malayalam
from playsound import playsound  # pip install playsound==1.2.2
from face import HandGestureDetector
import threading

CAMERA_URL = "http://10.127.141.132:8080/video"

try:
    import pyaudio
except ImportError:
    print("PyAudio is not installed. Please install it with 'pip install pyaudio'.")
    exit(1)

# ✅ Your API key (make sure it's valid)
GEMINI_API_KEY = "AIzaSyCwO_62w76l3D9yk0JxsfSmXtGtugszKdY"

# ✅ Arduino Serial Setup
ARDUINO_PORT = "/dev/ttyACM1"  # Change this to your Arduino port (COM3, COM4, etc. on Windows or /dev/ttyUSB0 on Linux)
BAUD_RATE = 9600

# Global variables to store gesture results
last_gesture_result = "none"  # Simple: "wave", "gun", or "none"
gesture_detection_active = False
live_gesture_callback = None  # Callback function for live results

# Initialize Arduino connection
try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    print(f"✅ Connected to Arduino on {ARDUINO_PORT}")
    
    # Send initial suspect emotion (3) command on boot
    arduino.write("3\n".encode())
    print("🤖 Sent initial suspect emotion (3) to Arduino on boot")
    
except Exception as e:
    print(f"❌ Arduino connection failed: {e}")
    arduino = None

# ✅ Fixed and improved prompt
ROASTIMACHI_PROMPT = """
നീ ഒരു roasting expert ആണ്. എല്ലാ reply കളും Malayalam-ൽ male tone-ൽ വേണം.
Rules:
1. എപ്പോഴും roasted replies മാത്രം - very short and witty
2. Malayalam movie dialogues, local slang use ചെയ്യാം
3. Examples:
   - "പഠിക്കാൻ പോകുന്നു" എന്ന് പറഞ്ഞാൽ: "പഠിക്കാനോ? നിന്റെ തലയിൽ എന്താ ഉള്ളേ?"
   - "Hello" എന്ന് പറഞ്ഞാൽ: "എന്താ ചേട്ടാ, വേറെ വേല ഒന്നും ഇല്ലേ?"
   - Problems പറഞ്ഞാൽ: "എനിക്ക് അറിയാം നിനക്ക് കഴിവ് ഇല്ലന്ന്"
4. Only Malayalam language use ചെയ്യണം
5. Maximum 1-2 sentences മാത്രം
"""

def send_emotion_to_arduino(emotion_code):
    """Send emotion code to Arduino"""
    if arduino:
        try:
            arduino.write(f"{emotion_code}\n".encode())
            print(f"🤖 Sent emotion {emotion_code} to Arduino")
        except Exception as e:
            print(f"❌ Failed to send to Arduino: {e}")
    else:
        print(f"🤖 Would send emotion {emotion_code} (Arduino not connected)")

def analyze_emotion_from_response(response_text):
    """Analyze the roast response and determine appropriate emotion"""
    response_lower = response_text.lower()
    
    # Emotion mapping based on roast intensity/type
    if any(word in response_lower for word in ['കഴിവ് ഇല്ല', 'മോശം', 'പ്രശ്നം', 'കുഴപ്പം']):
        return "4"  # Angry - for harsh roasts
    elif any(word in response_lower for word in ['എന്തോ', 'അറിയില്ല', 'കൺഫ്യൂഷൻ']):
        return "5"  # Dizzy - for confused responses  
    elif any(word in response_lower for word in ['സംശയം', 'എന്താ', 'വിചിത്രം']):
        return "3"  # Suspect - for suspicious/questioning roasts
    elif any(word in response_lower for word in ['പൊളിച്ചു', 'നല്ലത്', 'കൊള്ളാം']):
        return "2"  # Happy - for lighter roasts
    else:
        return "1"  # Blink - default for normal roasts

def call_gemini_api(user_prompt):
    """Call Gemini API with better error handling"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"{ROASTIMACHI_PROMPT}\n\nUser said: {user_prompt}\n\nRoast response in Malayalam:"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 100,  # Keep responses short
            "topP": 1.0
        }
    }
    
    try:
        print(f"🌐 Sending to Gemini: {user_prompt}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                print(f"✅ Raw Gemini Response: {text}")
                return text
            else:
                print("❌ No candidates in response")
                return "എന്റെ പൊന്നോ, എന്തോ പ്രശ്നം ഉണ്ട്!"
        else:
            print(f"❌ Gemini API Error: {response.status_code}")
            print(f"Error details: {response.text}")
            return "API-യിൽ എന്തോ കുഴപ്പം. നിന്റെ കർമ്മം!"
            
    except requests.exceptions.Timeout:
        return "വൈകി പോയി! സമയം കളഞ്ഞു!"
    except Exception as e:
        print(f"❌ Exception: {e}")
        return "എന്തോ error വന്നു. നിന്റെ ഭാഗ്യം!"

def run_live_gesture_detection():
    """Run LIVE gesture detection that returns results immediately"""
    global last_gesture_result, gesture_detection_active
    
    try:
        print("📹 Starting LIVE camera detection...")
        detector = HandGestureDetector(CAMERA_URL)
        
        if not detector.test_connection():
            print("❌ Camera connection failed")
            return "none"
        
        print("✅ Camera connected! LIVE gesture detection active...")
        print("👋 Make gestures - results will appear immediately!")
        print("Press 'q' to stop detection")
        
        gesture_detection_active = True
        
        # Override detection methods for live results
        original_wave_method = detector.analyze_wave_motion
        original_gun_method = detector.analyze_gun_gestures
        
        def live_wave_detection(current_positions, frame):
            global last_gesture_result
            old_count = detector.wave_count
            result = original_wave_method(current_positions, frame)
            
            # Check if new wave detected
            if detector.wave_count > old_count:
                last_gesture_result = "wave"
                print(f"🔴 LIVE: WAVE detected! (Total: {detector.wave_count})")
                send_emotion_to_arduino("2")  # Happy
                
                # Call callback if provided
                if live_gesture_callback:
                    live_gesture_callback("wave")
                    
            return result
        
        def live_gun_detection(gun_confidences, frame):
            global last_gesture_result
            old_count = detector.gun_count
            original_gun_method(gun_confidences, frame)
            
            # Check if new gun gesture detected
            if detector.gun_count > old_count:
                last_gesture_result = "gun"
                print(f"🔴 LIVE: GUN detected! (Total: {detector.gun_count})")
                send_emotion_to_arduino("4")  # Angry
                
                # Call callback if provided
                if live_gesture_callback:
                    live_gesture_callback("gun")
        
        # Apply live detection
        detector.analyze_wave_motion = live_wave_detection
        detector.analyze_gun_gestures = live_gun_detection
        
        # Run detection (this will give live results)
        detector.start_detection()
        
        return last_gesture_result
            
    except Exception as e:
        print(f"❌ Live gesture detection error: {e}")
        return "none"
    finally:
        gesture_detection_active = False

def set_live_gesture_callback(callback_function):
    """Set a callback function to receive live gesture results"""
    global live_gesture_callback
    live_gesture_callback = callback_function
    print("✅ Live gesture callback set!")

def get_live_gesture():
    """Get the most recent live gesture: 'wave', 'gun', or 'none'"""
    return last_gesture_result

def on_gesture_detected(gesture):
    """Callback function that gets called when gesture is detected live"""
    print(f"🔥 LIVE CALLBACK: {gesture.upper()} gesture detected!")
    
    # You can add any custom logic here
    if gesture == "wave":
        print("   → Processing wave gesture...")
    elif gesture == "gun":
        print("1")
        arduino.write("2\n".encode())
        playsound("glass.mp3")
        
    # Example: Send to speech or other systems immediately
    return gesture

def speech_to_text():
    """Main speech recognition loop with better error handling"""
    recognizer = sr.Recognizer()
    
    # Adjust for ambient noise
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
    
    print("🎙️ Ready! Speak something in Malayalam... Ctrl+C to exit.")
    print("💡 Say 'ക്യാമറ' to start gesture detection")
    
    while True:
        try:
            with sr.Microphone() as source:
                print("\n👂 Listening...")
                # Longer timeout for better recognition
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            print("🔄 Processing speech...")
            text = recognizer.recognize_google(audio, language="ml-IN")
            print(f"📝 You said: {text}")

            # Special case for hello
            if "ഹലോ" in text.lower() or "hello" in text.lower():
                print("🎵 Playing hello.mp3...")
                try:
                    playsound("hello.mp3")
                except:
                    print("❌ Could not play hello.mp3")
                continue
            
            # Camera/gesture detection trigger
            elif "ക്യാമറ" in text.lower() or "camera" in text.lower():
                print("📹 Starting LIVE gesture detection...")
                
                # Set up live callback
                set_live_gesture_callback(on_gesture_detected)
                
                # Run LIVE gesture detection in separate thread
                gesture_thread = threading.Thread(target=run_live_gesture_detection)
                gesture_thread.daemon = True
                gesture_thread.start()
                
                print("🔴 LIVE detection active! Gestures will be detected immediately.")
                print("💡 Say 'stop camera' to end detection")
                continue
            
            # Stop camera detection
            elif "stop camera" in text.lower() or "സ്റ്റോപ്പ് ക്യാമറ" in text.lower():
                gesture_detection_active = False
                current_gesture = get_live_gesture()
                print(f"⏹️ Camera stopped. Last gesture: {current_gesture}")
                
                feedback = f"Camera stopped ചെയ്തു. Last gesture: {current_gesture}"
                try:
                    speak_malayalam(feedback)
                except Exception as e:
                    print(f"❌ TTS Error: {e}")
                continue
            
            # Check if asking about live gesture
            elif "gesture" in text.lower() or "ജെസ്‌ചർ" in text.lower():
                current_gesture = get_live_gesture()
                print(f"📊 Current live gesture: {current_gesture}")
                
                # Send to Gemini with gesture context
                gemini_input = f"{text}. (Current gesture: {current_gesture})"
                gemini_response = call_gemini_api(gemini_input)
                print(f"🧠 Gemini response: {gemini_response}")
                
                # Analyze emotion and send to Arduino
                emotion = analyze_emotion_from_response(gemini_response)
                send_emotion_to_arduino(emotion)

                # Speak back using TTS 
                try:
                    speak_malayalam(gemini_response)
                except Exception as e:
                    print(f"❌ TTS Error: {e}")
                continue
            
            # Regular text processing
            # Send to Gemini
            gemini_response = call_gemini_api(text)
            print(f"🧠 Gemini response: {gemini_response}")

            # Analyze emotion and send to Arduino
            emotion = analyze_emotion_from_response(gemini_response)
            send_emotion_to_arduino(emotion)

            # Speak back using TTS 
            try:
                speak_malayalam(gemini_response)
            except Exception as e:
                print(f"❌ TTS Error: {e}")

        except sr.WaitTimeoutError:
            print("⏰ No speech detected. Listening again...")
            continue
        except sr.UnknownValueError:
            print("❌ Sorry, couldn't understand. Try speaking clearly in Malayalam.")
            continue
        except sr.RequestError as e:
            print(f"❌ Speech Recognition API Error: {e}")
            continue
        except KeyboardInterrupt:
            print("\n👋 Exiting... Bye!")
            # Print current live gesture
            current_gesture = get_live_gesture()
            print(f"📊 Current Live Gesture: {current_gesture}")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            continue

def test_arduino_emotions():
    """Test all Arduino emotions"""
    emotions = {
        "1": "Blink",
        "2": "Happy", 
        "3": "Suspect",
        "4": "Angry",
        "5": "Dizzy"
    }
    
    print("🧪 Testing Arduino emotions...")
    for code, name in emotions.items():
        print(f"Testing {name} (code {code})")
        send_emotion_to_arduino(code)
        time.sleep(3)  # Wait 3 seconds between emotions

def test_live_gesture_detection():
    """Test LIVE gesture detection"""
    print("🧪 Testing LIVE gesture detection...")
    
    # Set up callback for testing
    def test_callback(gesture):
        print(f"🧪 TEST CALLBACK: {gesture} detected!")
        return gesture
    
    set_live_gesture_callback(test_callback)
    
    # Run live detection
    run_live_gesture_detection()
    
    return get_live_gesture()

def test_gemini_directly():
    """Test function to check if Gemini API is working"""
    print("🧪 Testing Gemini API directly...")
    test_response = call_gemini_api("ഹലോ")
    print(f"Test response: {test_response}")
    
    # Test emotion detection
    emotion = analyze_emotion_from_response(test_response)
    print(f"Detected emotion: {emotion}")
    send_emotion_to_arduino(emotion)

if __name__ == "__main__":
    # Uncomment to test Arduino emotions
    # test_arduino_emotions()
    
    # Uncomment to test Gemini API first
    # test_gemini_directly()
    
    # Uncomment to test LIVE gesture detection
    # test_live_gesture_detection()
    
    # Main program
    speech_to_text()