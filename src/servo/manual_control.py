import time
import picod
import os
import sys
import signal
import tty
import termios
import select

class GracefulExit(Exception):
    pass

def signal_handler(signum, frame):
    raise GracefulExit()

class NonBlockingInput:
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        
    def __enter__(self):
        tty.setraw(self.fd)
        return self
        
    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def get_char(self):
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None

class ServoController:
    def __init__(self):
        self.pico = picod.pico()
        if not self.pico.connected:
            raise Exception("Failed to connect to Pico")
            
        self.servos = {
            1: {
                "pin": 21,
                "name": "Base",
                "position": 1490,
                "min": 500,
                "max": 2500,
                "center": 1490,
                "step": 50
            },
            2: {
                "pin": 22,
                "name": "Second",
                "position": 1540,
                "min": 1540,
                "max": 2500,
                "center": 2020,
                "step": 50
            },
            3: {
                "pin": 3,
                "name": "Third",
                "position": 1840,
                "min": 1840,
                "max": 2500,
                "center": 2170,
                "step": 50
            },
            4: {
                "pin": 4,
                "name": "Fourth",
                "position": 925,
                "min": 500,
                "max": 1350,
                "center": 925,
                "step": 50
            },
            5: {
                "pin": 5,
                "name": "Wrist",
                "position": 1500,
                "min": 500,
                "max": 2500,
                "center": 1500,
                "step": 50
            }
        }

        self.current_servo = 1
        self.running = True
        
        # Initialize servos
        for servo in self.servos.values():
            self.pico.tx_servo(servo["pin"], servo["position"])
            time.sleep(0.1)

    def move_servo(self, servo_id, new_position):
        """Move a servo to an absolute position"""
        servo = self.servos[servo_id]
        if servo["min"] <= new_position <= servo["max"]:
            servo["position"] = new_position
            self.pico.tx_servo(servo["pin"], new_position)
            return True
        return False

    def handle_input(self, char):
        """Handle keyboard input"""
        if char == 'q':
            self.running = False
        elif char == 'c':
            # Center current servo
            servo = self.servos[self.current_servo]
            self.move_servo(self.current_servo, servo["center"])
        elif char == '\x1b':
            # Handle arrow keys
            next_char = sys.stdin.read(2)
            if next_char == '[A':  # Up arrow
                self.current_servo = max(1, self.current_servo - 1)
            elif next_char == '[B':  # Down arrow
                self.current_servo = min(5, self.current_servo + 1)
            elif next_char == '[D':  # Left arrow
                servo = self.servos[self.current_servo]
                new_pos = servo["position"] - servo["step"]
                self.move_servo(self.current_servo, new_pos)
            elif next_char == '[C':  # Right arrow
                servo = self.servos[self.current_servo]
                new_pos = servo["position"] + servo["step"]
                self.move_servo(self.current_servo, new_pos)
        elif char in ['+', '=']:
            servo = self.servos[self.current_servo]
            servo["step"] = min(100, servo["step"] + 10)
        elif char == '-':
            servo = self.servos[self.current_servo]
            servo["step"] = max(10, servo["step"] - 10)

    def update_display(self):
        """Update the display with current servo information"""
        os.system('clear')
        print("\n=== Servo Control ===")
        print("\nSelected Servo:")
        servo = self.servos[self.current_servo]
        print(f"  Servo {self.current_servo}: {servo['name']}")
        print(f"  Position: {servo['position']}µs")
        print(f"  Range: {servo['min']} - {servo['max']}µs")
        print(f"  Step size: {servo['step']}µs")
        
        print("\nAll Servos:")
        for id, s in self.servos.items():
            marker = ">" if id == self.current_servo else " "
            print(f"{marker} {id}: {s['name']} = {s['position']}µs")
        
        print("\nControls:")
        print("  ↑/↓ : Select servo")
        print("  ←/→ : Adjust position")
        print("  C   : Center servo")
        print("  +/- : Adjust step size")
        print("  Q   : Quit")

    def cleanup(self):
        """Clean up before exit"""
        print("\nMoving to center positions...")
        for servo in self.servos.values():
            self.pico.tx_servo(servo["pin"], servo["center"])
            time.sleep(0.2)
        time.sleep(0.5)
        for servo in self.servos.values():
            self.pico.tx_servo(servo["pin"], 0)
        self.pico.close()

def main():
    controller = None
    try:
        signal.signal(signal.SIGINT, signal_handler)
        controller = ServoController()
        
        with NonBlockingInput() as keyboard:
            while controller.running:
                controller.update_display()
                char = keyboard.get_char()
                if char:
                    controller.handle_input(char)
                time.sleep(0.1)
            
    except GracefulExit:
        print("\nReceived Ctrl+C, shutting down gracefully...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if controller:
            controller.cleanup()
        print("Program terminated")

if __name__ == "__main__":
    main()