import time
import picod
import os
import sys
import signal
import math
import curses

class GracefulExit(Exception):
    pass

def signal_handler(signum, frame):
    raise GracefulExit()

class DemoController:
    def __init__(self, screen):
        self.screen = screen
        self.pico = picod.pico()
        if not self.pico.connected:
            raise Exception("Failed to connect to Pico")
            
        self.servos = {
            1: {
                "pin": 21,
                "name": "Base (MG996)",
                "position": 1490,
                "min": 500,
                "max": 2500,
                "center": 1490,
                "config": {"type": "servo", "freq": 50, "min": 500, "max": 2500}
            },
            2: {
                "pin": 22,
                "name": "Second (MG996)",
                "position": 1540,
                "min": 1540,
                "max": 2500,
                "center": 2020,
                "config": {"type": "servo", "freq": 50, "min": 500, "max": 2500}
            },
            3: {
                "pin": 3,
                "name": "Third (20kg)",
                "position": 1840,
                "min": 1840,
                "max": 2500,
                "center": 2170,
                "config": {"type": "servo", "freq": 50, "min": 500, "max": 2500}
            },
            4: {
                "pin": 4,
                "name": "Fourth (25kg)",
                "position": 925,
                "min": 500,
                "max": 1350,
                "center": 925,
                "config": {"type": "servo", "freq": 50, "min": 500, "max": 2500}
            },
            5: {
                "pin": 5,
                "name": "Wrist (MG90S)",
                "position": 1500,
                "min": 500,
                "max": 2500,
                "center": 1500,
                "config": {"type": "servo", "freq": 50, "min": 500, "max": 2500}
            }
        }

        # Demo settings
        self.demo_active = False
        self.pattern = 'dance'
        self.start_time = time.time()
        self.speed = 1.0
        self.running = True
        
        # Initialize screen
        curses.curs_set(0)
        self.screen.nodelay(1)
        
        # Initialize servos with a delay between each
        for servo in self.servos.values():
            # First disable the pin
            self.pico.tx_servo(servo["pin"], 0)
            time.sleep(0.1)
            # Then initialize with position
            self.pico.tx_servo(servo["pin"], servo["position"])
            time.sleep(0.2)  # Longer delay between servos

    def move_servo(self, servo_id, new_position):
        """Move a servo to an absolute position"""
        servo = self.servos[servo_id]
        if servo["min"] <= new_position <= servo["max"]:
            servo["position"] = new_position
            self.pico.tx_servo(servo["pin"], new_position)
            
            self.screen.move(12, 0)
            self.screen.clrtoeol()
            self.screen.addstr(12, 0, f"Servo {servo_id} ({servo['name']}): {new_position}µs")
            self.screen.refresh()
            return True
        return False

    def update_demo(self):
        """Update servo positions based on current pattern"""
        t = (time.time() - self.start_time) * self.speed

        if self.pattern == 'dance':
            # Complex dance pattern using all servos
            base_pos = 1490 + int(500 * math.sin(t))  # Smooth side to side
            second_pos = 2020 + int(200 * math.sin(t * 1.5))  # Faster up/down
            third_pos = 2170 + int(150 * math.sin(t * 0.75))  # Slower complementary
            fourth_pos = 925 + int(200 * math.sin(t * 2))  # Quick movements
            wrist_pos = 1500 + int(400 * math.sin(t * 1.25))  # Medium speed rotation
            
            # Add small delays between servo movements
            self.move_servo(1, base_pos)
            time.sleep(0.01)
            self.move_servo(2, second_pos)
            time.sleep(0.01)
            self.move_servo(3, third_pos)
            time.sleep(0.01)
            self.move_servo(4, fourth_pos)
            time.sleep(0.01)
            self.move_servo(5, wrist_pos)

        elif self.pattern == 'circle':
            base_pos = 1490 + int(500 * math.sin(t))
            second_pos = 2020 + int(200 * math.cos(t))
            
            self.move_servo(1, base_pos)
            time.sleep(0.01)
            self.move_servo(2, second_pos)

        elif self.pattern == 'wave':
            pos = 2020 + int(200 * math.sin(t))
            self.move_servo(2, pos)

        elif self.pattern == 'scan':
            base_pos = 1490 + int(800 * math.sin(t * 0.5))
            self.move_servo(1, base_pos)

    def toggle_demo(self):
        """Toggle demo mode on/off"""
        self.demo_active = not self.demo_active
        self.start_time = time.time()
        msg = "Demo " + ("started" if self.demo_active else "stopped")
        self.screen.addstr(13, 0, msg)
        self.screen.refresh()

    def change_pattern(self):
        """Change to next pattern"""
        patterns = ['dance', 'circle', 'wave', 'scan']
        current_idx = patterns.index(self.pattern)
        self.pattern = patterns[(current_idx + 1) % len(patterns)]
        self.start_time = time.time()
        msg = f"Changed to {self.pattern} pattern"
        self.screen.addstr(13, 0, msg)
        self.screen.refresh()

    def change_speed(self, faster=True):
        """Change demo speed"""
        if faster:
            self.speed = min(3.0, self.speed * 1.2)
        else:
            self.speed = max(0.3, self.speed / 1.2)
        msg = f"Speed: {self.speed:.1f}x"
        self.screen.addstr(13, 0, msg)
        self.screen.refresh()

    def cleanup(self):
        """Clean up before exit"""
        curses.endwin()
        print("\nMoving to center positions...")
        for servo in self.servos.values():
            self.pico.tx_servo(servo["pin"], servo["center"])
            time.sleep(0.2)
        time.sleep(0.5)
        for servo in self.servos.values():
            self.pico.tx_servo(servo["pin"], 0)
        self.pico.close()

def draw_menu(screen):
    """Draw the menu on the screen"""
    screen.addstr(0, 0, "Demo Movement Controller")
    screen.addstr(1, 0, "----------------------")
    screen.addstr(2, 0, "Controls:")
    screen.addstr(3, 0, "  t: Toggle demo")
    screen.addstr(4, 0, "  p: Change pattern")
    screen.addstr(5, 0, "  +: Speed up")
    screen.addstr(6, 0, "  -: Slow down")
    screen.addstr(7, 0, "  q: Quit")
    screen.addstr(8, 0, "\nPatterns:")
    screen.addstr(9, 0, "  - Dance: Coordinated movement of all servos")
    screen.addstr(10, 0, "  - Circle: Base + Second joint circular motion")
    screen.addstr(11, 0, "  - Wave: Up/down waving motion")
    screen.refresh()

def main(screen):
    controller = None
    try:
        signal.signal(signal.SIGINT, signal_handler)
        draw_menu(screen)
        controller = DemoController(screen)
        
        while controller.running:
            if controller.demo_active:
                controller.update_demo()
            
            # Check for key input
            try:
                key = screen.getch()
                if key != -1:  # -1 means no key pressed
                    if key == ord('q'):
                        break
                    elif key == ord('t'):
                        controller.toggle_demo()
                    elif key == ord('p'):
                        controller.change_pattern()
                    elif key in [ord('+'), ord('=')]:
                        controller.change_speed(faster=True)
                    elif key == ord('-'):
                        controller.change_speed(faster=False)
            except curses.error:
                pass
                
            time.sleep(0.01)
            
    except GracefulExit:
        pass
    except Exception as e:
        curses.endwin()
        print(f"\nError: {e}")
    finally:
        if controller:
            controller.cleanup()
        print("Program terminated")

if __name__ == "__main__":
    curses.wrapper(main)