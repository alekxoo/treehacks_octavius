import time
import picod
import sys
import signal

class GracefulExit(Exception):
    pass

def signal_handler(signum, frame):
    raise GracefulExit()

class PWMTester:
    def __init__(self):
        self.pico = picod.pico()
        if not self.pico.connected:
            raise Exception("Failed to connect to Pico")
        
        # Define all servos
        self.servos = {
            1: {"pin": 7, "name": "Base"},
            2: {"pin": 8, "name": "Second"},
            3: {"pin": 5, "name": "Third"},
            4: {"pin": 10, "name": "Fourth"},
            5: {"pin": 11, "name": "Wrist"}
        }
        
        # Initialize each servo pin explicitly
        print("Initializing servo pins...")
        for servo in self.servos.values():
            print(f"Setting up pin {servo['pin']} for {servo['name']}")
            self.pico.tx_servo(servo['pin'], 1500)  # Center position
            time.sleep(0.1)  # Small delay between initializations
        
    def test_sequence(self):
        """Test all servos in sequence"""
        try:
            while True:
                # Move each servo independently
                for servo_id, servo in self.servos.items():
                    print(f"\nTesting {servo['name']} (Pin {servo['pin']}):")
                    
                    # Test movement range
                    positions = [1000, 1500, 2000]
                    for pos in positions:
                        print(f"Moving to position {pos}...")
                        self.pico.tx_servo(servo['pin'], pos)
                        time.sleep(0.5)  # Give servo time to move
                    
                    print(f"Completed test of {servo['name']}")
                    time.sleep(0.5)  # Delay between servos
                
                # Now test all servos moving together
                print("\nTesting all servos together...")
                for pos in [1000, 1500, 2000]:
                    print(f"\nMoving all servos to {pos}")
                    for servo in self.servos.values():
                        self.pico.tx_servo(servo['pin'], pos)
                        time.sleep(0.05)  # Small delay between each servo
                    time.sleep(1)  # Wait for movement to complete
                
                retry = input("\nTest another cycle? (y/n): ").lower()
                if retry != 'y':
                    break
                    
        except Exception as e:
            print(f"Error during test: {e}")

    def cleanup(self):
        print("\nCleaning up...")
        for servo in self.servos.values():
            print(f"Stopping PWM on pin {servo['pin']}")
            self.pico.tx_servo(servo['pin'], 0)
            time.sleep(0.1)
        self.pico.close()

def main():
    tester = None
    try:
        signal.signal(signal.SIGINT, signal_handler)
        
        print("\nMultiple Servo Tester")
        print("-------------------")
        print("This script will test each servo individually")
        print("and then test all servos together.")
        
        input("\nPress Enter to start testing...")
        
        tester = PWMTester()
        tester.test_sequence()
            
    except GracefulExit:
        print("\nReceived Ctrl+C, shutting down gracefully...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if tester:
            tester.cleanup()
        print("Test completed")

if __name__ == "__main__":
    main()