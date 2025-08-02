import cv2
import time
import requests
import threading
from queue import Queue
import numpy as np
import mediapipe as mp
from collections import deque
import math

class HandGestureDetector:
    def __init__(self, ip_url):
        self.ip_url = ip_url
        
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Wave detection parameters
        self.wave_threshold = 30  # Minimum movement for wave detection
        self.wave_frames_required = 8  # Frames needed to confirm a wave
        self.position_history = deque(maxlen=15)  # Store recent hand positions
        
        # Gun gesture detection parameters
        self.gun_confidence_threshold = 0.8  # Confidence needed for gun detection
        self.gun_hold_frames = 5  # Frames to hold gun gesture for confirmation
        self.gun_history = deque(maxlen=10)  # Store recent gun detection results
        
        # Detection states
        self.wave_detected = False
        self.gun_detected = False
        self.wave_start_time = 0
        self.gun_start_time = 0
        self.wave_count = 0
        self.gun_count = 0
        self.last_wave_time = 0
        self.last_gun_time = 0
        
        # Performance settings
        self.target_width = 640
        self.process_every_n_frames = 1  # Process every frame for smooth tracking
        
        # Threading for frame capture
        self.frame_queue = Queue(maxsize=2)
        self.stop_capture = False
        self.capture_thread = None
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0
        
    def test_connection(self):
        """Test if the IP camera is accessible"""
        print(f"🔍 Testing connection to: {self.ip_url}")
        
        try:
            response = requests.get(self.ip_url, timeout=5, stream=True)
            if response.status_code == 200:
                print("✅ HTTP connection successful!")
                
                cap = cv2.VideoCapture(self.ip_url)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        print(f"✅ Camera connected! Resolution: {width}x{height}")
                        cap.release()
                        return True
                    else:
                        print("❌ Connected but cannot read frames")
                        cap.release()
                        return False
                else:
                    print("❌ OpenCV cannot connect to camera")
                    return False
            else:
                print(f"❌ HTTP Error {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def capture_frames(self, cap):
        """Threaded frame capture"""
        while not self.stop_capture:
            ret, frame = cap.read()
            if ret:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
                else:
                    try:
                        self.frame_queue.get_nowait()
                    except:
                        pass
                    self.frame_queue.put(frame)
            else:
                time.sleep(0.01)
    
    def resize_frame(self, frame):
        """Resize frame for faster processing"""
        height, width = frame.shape[:2]
        if width > self.target_width:
            ratio = self.target_width / width
            new_height = int(height * ratio)
            frame = cv2.resize(frame, (self.target_width, new_height), interpolation=cv2.INTER_LINEAR)
        return frame
    
    def detect_gun_gesture(self, hand_landmarks, frame, hand_idx):
        """Detect gun gesture (pointing with index finger)"""
        try:
            h, w, _ = frame.shape
            
            # Get key landmarks
            landmarks = hand_landmarks.landmark
            
            # Finger tip and pip (joint) positions
            index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_pip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
            index_mcp = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]
            
            middle_tip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            middle_pip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
            
            ring_tip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP]
            ring_pip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_PIP]
            
            pinky_tip = landmarks[self.mp_hands.HandLandmark.PINKY_TIP]
            pinky_pip = landmarks[self.mp_hands.HandLandmark.PINKY_PIP]
            
            thumb_tip = landmarks[self.mp_hands.HandLandmark.THUMB_TIP]
            thumb_ip = landmarks[self.mp_hands.HandLandmark.THUMB_IP]
            
            wrist = landmarks[self.mp_hands.HandLandmark.WRIST]
            
            # Convert to pixel coordinates
            def to_pixel(landmark):
                return (int(landmark.x * w), int(landmark.y * h))
            
            index_tip_px = to_pixel(index_tip)
            index_mcp_px = to_pixel(index_mcp)
            wrist_px = to_pixel(wrist)
            
            # Gun gesture criteria:
            gun_score = 0
            max_score = 5
            
            # 1. Index finger extended (tip further from wrist than MCP)
            index_extended = self.distance(index_tip, wrist) > self.distance(index_mcp, wrist)
            if index_extended:
                gun_score += 1
            
            # 2. Middle finger folded (tip closer to wrist than PIP)
            middle_folded = self.distance(middle_tip, wrist) < self.distance(middle_pip, wrist)
            if middle_folded:
                gun_score += 1
            
            # 3. Ring finger folded
            ring_folded = self.distance(ring_tip, wrist) < self.distance(ring_pip, wrist)
            if ring_folded:
                gun_score += 1
            
            # 4. Pinky folded
            pinky_folded = self.distance(pinky_tip, wrist) < self.distance(pinky_pip, wrist)
            if pinky_folded:
                gun_score += 1
            
            # 5. Thumb extended (can be up or to the side)
            thumb_extended = self.distance(thumb_tip, wrist) > self.distance(thumb_ip, wrist)
            if thumb_extended:
                gun_score += 1
            
            # Calculate confidence
            confidence = gun_score / max_score
            
            # Draw gun gesture analysis
            analysis_text = f"Gun: {confidence:.1f}"
            cv2.putText(frame, analysis_text, (index_tip_px[0]-30, index_tip_px[1]-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Draw pointing direction line if gun detected
            if confidence >= self.gun_confidence_threshold:
                # Calculate pointing direction
                direction_x = index_tip_px[0] - index_mcp_px[0]
                direction_y = index_tip_px[1] - index_mcp_px[1]
                
                # Extend the line to show pointing direction
                line_length = 100
                if direction_x != 0 or direction_y != 0:
                    norm = math.sqrt(direction_x**2 + direction_y**2)
                    direction_x = int(direction_x / norm * line_length)
                    direction_y = int(direction_y / norm * line_length)
                    
                    end_point = (index_tip_px[0] + direction_x, index_tip_px[1] + direction_y)
                    cv2.arrowedLine(frame, index_tip_px, end_point, (0, 0, 255), 3, tipLength=0.3)
                
                # Add gun gesture label
                cv2.putText(frame, 'GUN!', (index_tip_px[0]-20, index_tip_px[1]-50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            return confidence
            
        except Exception as e:
            print(f"Gun gesture detection error: {e}")
            return 0.0
    
    def distance(self, point1, point2):
        """Calculate Euclidean distance between two landmarks"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def detect_hands_and_gestures(self, frame):
        """Detect hands and analyze for gestures"""
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        current_positions = []
        gun_confidences = []
        
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
                
                # Get hand center position for wave detection
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h, w, _ = frame.shape
                wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                tip_x, tip_y = int(index_tip.x * w), int(index_tip.y * h)
                
                center_x = (wrist_x + tip_x) // 2
                center_y = (wrist_y + tip_y) // 2
                current_positions.append((center_x, center_y))
                
                # Detect gun gesture
                gun_confidence = self.detect_gun_gesture(hand_landmarks, frame, i)
                gun_confidences.append(gun_confidence)
                
                # Draw hand center
                cv2.circle(frame, (center_x, center_y), 8, (255, 255, 0), -1)
                cv2.putText(frame, f'Hand {i+1}', (center_x-30, center_y-20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Analyze wave motion
        self.analyze_wave_motion(current_positions, frame)
        
        # Analyze gun gestures
        self.analyze_gun_gestures(gun_confidences, frame)
        
        return frame, len(current_positions)
    
    def analyze_wave_motion(self, current_positions, frame):
        """Analyze hand positions for waving motion"""
        if not current_positions:
            if len(self.position_history) > 0:
                self.position_history.clear()
            self.wave_detected = False
            return
        
        timestamp = time.time()
        self.position_history.append((current_positions, timestamp))
        
        if len(self.position_history) < self.wave_frames_required:
            return
        
        for hand_idx in range(len(current_positions)):
            if self.detect_wave_for_hand(hand_idx, frame):
                current_time = time.time()
                
                if current_time - self.last_wave_time > 1.0:
                    self.wave_count += 1
                    self.last_wave_time = current_time
                    self.wave_detected = True
                    self.wave_start_time = current_time
                    print(f"👋 WAVE DETECTED! Count: {self.wave_count}")
                    return "wave"
    
    def analyze_gun_gestures(self, gun_confidences, frame):
        """Analyze gun gestures"""
        current_time = time.time()
        
        # Check if any hand shows gun gesture
        max_confidence = max(gun_confidences) if gun_confidences else 0.0
        
        # Add to history
        self.gun_history.append(max_confidence >= self.gun_confidence_threshold)
        
        # Check if gun gesture is held for required frames
        if len(self.gun_history) >= self.gun_hold_frames:
            recent_guns = list(self.gun_history)[-self.gun_hold_frames:]
            consistent_gun = sum(recent_guns) >= self.gun_hold_frames * 0.8  # 80% of frames
            
            if consistent_gun and current_time - self.last_gun_time > 1.5:  # 1.5 second cooldown
                self.gun_count += 1
                self.last_gun_time = current_time
                self.gun_detected = True
                self.gun_start_time = current_time
                print(f"🔫 GUN GESTURE DETECTED! Count: {self.gun_count}")
    
    def detect_wave_for_hand(self, hand_idx, frame):
        """Detect waving motion for a specific hand"""
        try:
            recent_positions = []
            for positions_list, timestamp in list(self.position_history):
                if hand_idx < len(positions_list):
                    recent_positions.append(positions_list[hand_idx])
            
            if len(recent_positions) < self.wave_frames_required:
                return False
            
            x_positions = [pos[0] for pos in recent_positions]
            y_positions = [pos[1] for pos in recent_positions]
            
            x_changes = []
            for i in range(1, len(x_positions)):
                x_changes.append(x_positions[i] - x_positions[i-1])
            
            direction_changes = 0
            for i in range(1, len(x_changes)):
                if (x_changes[i] > 0) != (x_changes[i-1] > 0):
                    direction_changes += 1
            
            x_range = max(x_positions) - min(x_positions)
            y_range = max(y_positions) - min(y_positions)
            
            is_wave = (
                x_range > self.wave_threshold and
                direction_changes >= 3 and
                x_range > y_range * 0.7
            )
            
            if hand_idx < len(recent_positions):
                pos = recent_positions[-1]
                cv2.putText(frame, f'Wave: H:{x_range:.0f} D:{direction_changes}', 
                           (pos[0]-60, pos[1]+60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                
                if is_wave:
                    cv2.putText(frame, 'WAVING!', (pos[0]-30, pos[1]+80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            return is_wave
            
        except Exception as e:
            return False
    
    def start_detection(self):
        """Start hand gesture detection"""
        if not self.test_connection():
            return False
            
        print(f"\n🤚 Starting Hand Gesture Detection with: {self.ip_url}")
        print("\n🎮 Controls:")
        print("  'q' or ESC  - Quit")
        print("  's'         - Save current frame")
        print("  'r'         - Reset counters")
        print("  'f'         - Toggle fullscreen")
        print("  '+'         - Increase wave sensitivity")
        print("  '-'         - Decrease wave sensitivity")
        print("  'g'         - Adjust gun detection sensitivity")
        
        cap = cv2.VideoCapture(self.ip_url)
        
        if not cap.isOpened():
            print("❌ Failed to open camera")
            return False
        
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.stop_capture = False
        self.capture_thread = threading.Thread(target=self.capture_frames, args=(cap,))
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        frame_count = 0
        is_fullscreen = False
        
        print("✅ Hand gesture detection started!")
        print("👋 Wave Detection: Side-to-side hand movement")
        print("🔫 Gun Detection: Point with index finger, other fingers folded")
        
        try:
            while True:
                try:
                    frame = self.frame_queue.get_nowait()
                except:
                    time.sleep(0.001)
                    continue
                
                frame_count += 1
                display_frame = self.resize_frame(frame.copy())
                
                if frame_count % self.process_every_n_frames == 0:
                    display_frame, hand_count = self.detect_hands_and_gestures(display_frame)
                else:
                    hand_count = 0
                
                self.update_fps()
                self.add_overlay(display_frame, hand_count)
                
                window_name = 'Hand Gesture Detection - Wave & Gun'
                cv2.imshow(window_name, display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:
                    break
                    
                elif key == ord('s'):
                    filename = f"gesture_capture_{int(time.time())}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"📸 Frame saved: {filename}")
                    
                elif key == ord('r'):
                    self.wave_count = 0
                    self.gun_count = 0
                    self.position_history.clear()
                    self.gun_history.clear()
                    print("🔄 All counters reset!")
                    
                elif key == ord('+') or key == ord('='):
                    self.wave_threshold = max(10, self.wave_threshold - 5)
                    print(f"📈 Wave sensitivity increased (threshold: {self.wave_threshold})")
                    
                elif key == ord('-'):
                    self.wave_threshold = min(100, self.wave_threshold + 5)
                    print(f"📉 Wave sensitivity decreased (threshold: {self.wave_threshold})")
                    
                elif key == ord('g'):
                    self.gun_confidence_threshold = 0.9 if self.gun_confidence_threshold < 0.9 else 0.6
                    print(f"🎯 Gun sensitivity: {self.gun_confidence_threshold:.1f}")
                    
                elif key == ord('f'):
                    if is_fullscreen:
                        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                        is_fullscreen = False
                        print("🪟 Windowed mode")
                    else:
                        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                        is_fullscreen = True
                        print("🖥️  Fullscreen mode")
        
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user (Ctrl+C)")
            
        finally:
            self.stop_capture = True
            if self.capture_thread:
                self.capture_thread.join(timeout=1)
            cap.release()
            cv2.destroyAllWindows()
            print(f"\n📊 Session Statistics:")
            print(f"   Total frames processed: {frame_count}")
            print(f"   Waves detected: {self.wave_count}")
            print(f"   Gun gestures detected: {self.gun_count}")
            print(f"   Final FPS: {self.current_fps:.1f}")
            
        return True
    
    def add_overlay(self, frame, hand_count):
        """Add information overlay"""
        height, width = frame.shape[:2]
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (400, 160), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        current_time = time.time()
        wave_active = self.wave_detected and (current_time - self.wave_start_time < 1.0)
        gun_active = self.gun_detected and (current_time - self.gun_start_time < 1.5)
        
        info_lines = [
            f"IP Camera: {self.ip_url.split('/')[-2]}",
            f"Hands Detected: {hand_count}",
            f"Waves Detected: {self.wave_count}",
            f"Gun Gestures: {self.gun_count}",
            f"FPS: {self.current_fps:.1f}",
            f"Wave Sensitivity: {self.wave_threshold}",
            f"Gun Sensitivity: {self.gun_confidence_threshold:.1f}",
            f"Status: {'WAVING!' if wave_active else 'GUN!' if gun_active else 'Monitoring...'}"
        ]
        
        for i, line in enumerate(info_lines):
            y_position = 15 + (i * 18)
            if i == 7:  # Status line
                color = (0, 255, 0) if wave_active else (0, 0, 255) if gun_active else (255, 255, 255)
            else:
                color = (255, 255, 255)
            cv2.putText(frame, line, (10, y_position), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
        
        # Status indicators
        if wave_active:
            pulse_intensity = int(127 + 128 * abs(np.sin(current_time * 10)))
            cv2.circle(frame, (width - 60, 30), 20, (0, pulse_intensity, 0), -1)
            cv2.putText(frame, '👋', (width - 70, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        if gun_active:
            pulse_intensity = int(127 + 128 * abs(np.sin(current_time * 8)))
            cv2.circle(frame, (width - 30, 30), 20, (0, 0, pulse_intensity), -1)
            cv2.putText(frame, '🔫', (width - 40, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        elif hand_count > 0:
            cv2.circle(frame, (width - 30, 30), 15, (0, 255, 255), -1)
        else:
            cv2.circle(frame, (width - 30, 30), 15, (128, 128, 128), -1)
        
        # Reset flags after display
        if wave_active and current_time - self.wave_start_time > 1.0:
            self.wave_detected = False
        if gun_active and current_time - self.gun_start_time > 1.5:
            self.gun_detected = False
    
    def update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time

def main():
    """Main function"""
    CAMERA_URL = "http://10.140.51.207:8080/video"
    
    print("🤚 IP Camera Hand Gesture Detection")
    print("=" * 50)
    print(f"Camera URL: {CAMERA_URL}")
    print("\n📋 Detects:")
    print("   👋 Wave Gesture - Side-to-side hand movement")
    print("   🔫 Gun Gesture - Point with index finger")
    print("\n📋 Requirements:")
    print("   pip install mediapipe opencv-python requests numpy")
    
    try:
        detector = HandGestureDetector(CAMERA_URL)
        success = detector.start_detection()
        
        if success:
            print("✅ Hand gesture detection completed!")
        else:
            print("❌ Detection failed!")
            
    except ImportError as e:
        if "mediapipe" in str(e):
            print("❌ MediaPipe not installed!")
            print("Install with: pip install mediapipe")
        else:
            print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()