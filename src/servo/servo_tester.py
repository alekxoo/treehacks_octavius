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
        
        # Using only pin 7 for testing
        self.test_pin = 5
        print(f"Initialized PWM tester on pin {self.test_pin}")
        
        # Test positions
        self.positions = [1000, 1500, 2000]
        
    def test_pwm(self):
        """Test PWM output with different positions"""
        try:
            while True:
                for pos in self.positions:
                    print(f"\nSending PWM signal: {pos}µs to pin {self.test_pin}")
                    self.pico.tx_servo(self.test_pin, pos)
                    
                    # Wait for user confirmation
                    input(f"Press Enter to try next position (current: {pos}µs)...")
                
                retry = input("\nTest another cycle? (y/n): ").lower()
                if retry != 'y':
                    break
                    
        except Exception as e:
            print(f"Error during PWM test: {e}")

    def cleanup(self):
        print("\nStopping PWM output...")
        self.pico.tx_servo(self.test_pin, 0)
        self.pico.close()

def main():
    tester = None
    try:
        signal.signal(signal.SIGINT, signal_handler)
        
        print("\nPWM Signal Tester")
        print("----------------")
        print("This script will send PWM signals to pin 7.")
        print("Connect different servos to pin 7 to test if they respond.")
        print("Positions tested: 1000µs, 1500µs, 2000µs")
        
        input("\nPress Enter to start testing...")
        
        tester = PWMTester()
        tester.test_pwm()
            
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