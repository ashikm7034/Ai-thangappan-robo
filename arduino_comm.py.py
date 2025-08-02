#!/usr/bin/env python3

import sys
import time

# Check for naming conflicts and import pyserial
try:
    # Remove any serial.py from the path to avoid conflicts
    sys.modules.pop('serial', None)
    import serial
    # Verify we have the right serial module
    if not hasattr(serial, 'Serial'):
        raise ImportError("Wrong serial module imported")
except ImportError as e:
    print("Error importing pyserial:")
    print("1. Make sure pyserial is installed: pip install pyserial")
    print("2. Check if you have a file named 'serial.py' in your directory and rename it")
    print("3. Try: pip uninstall serial pyserial && pip install pyserial")
    sys.exit(1)
    

def find_arduino_port():
    """Try to find Arduino port automatically on Linux"""
    import glob
    possible_ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    
    for port in possible_ports:
        try:
            test_connection = serial.Serial(port, 9600, timeout=1)
            test_connection.close()
            return port
        except:
            continue
    return None

def setup_arduino_connection(port=None, baud_rate=9600):
    """Set up serial connection to Arduino"""
    if port is None:
        port = find_arduino_port()
        if port is None:
            print("No Arduino found. Please specify port manually.")
            return None
    
    try:
        arduino = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print(f"Connected to Arduino on {port}")
        return arduino
    except Exception as e:
        print(f"Error connecting to Arduino on {port}: {e}")
        print("Available ports:")
        import glob
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        for p in ports:
            print(f"  {p}")
        return None

def send_command(arduino, command):
    """Send command (1 or 2) to Arduino"""
    if arduino and arduino.is_open:
        arduino.write(str(command).encode())
        print(f"Sent: {command}")
        
        # Optional: Read response from Arduino
        try:
            time.sleep(0.1)  # Give Arduino time to respond
            if arduino.in_waiting > 0:
                response = arduino.readline().decode().strip()
                if response:
                    print(f"Arduino response: {response}")
        except Exception as e:
            print(f"Error reading response: {e}")
    else:
        print("Arduino not connected")

def main():
    print("Arduino Communication Script")
    print("Looking for Arduino...")
    
    # Try to auto-detect Arduino port
    arduino = setup_arduino_connection()
    
    # If auto-detection fails, ask user for port
    if arduino is None:
        port = input("Enter Arduino port (e.g., /dev/ttyUSB0): ").strip()
        if port:
            arduino = setup_arduino_connection(port)
    
    if arduino:
        try:
            print("\nArduino connected! Enter commands:")
            print("1 = Turn LED ON")
            print("2 = Turn LED OFF") 
            print("q = Quit")
            
            while True:
                user_input = input("\nCommand: ").strip()
                
                if user_input.lower() == 'q':
                    break
                elif user_input in ['1', '2']:
                    send_command(arduino, user_input)
                else:
                    print("Please enter only 1, 2, or q")
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            if arduino and arduino.is_open:
                arduino.close()
            print("Connection closed")
    else:
        print("Failed to connect to Arduino")
        print("\nTroubleshooting:")
        print("1. Check Arduino is plugged in")
        print("2. Check you have permission: sudo usermod -a -G dialout $USER")
        print("3. Log out and back in after adding to dialout group")

if __name__ == "__main__":
    main()