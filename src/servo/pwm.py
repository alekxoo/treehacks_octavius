import time
import picod

# GPIO pin definitions
GPIO_1 = 5  # First servo
GPIO_2 = 6  # Second servo

# Pulse width constants (in microseconds)
CENTER_PW = 1500    # Stop position
SPEED = 100         # Speed factor
MAX_DEVIATION = 5   # Maximum deviation from center

def main():
    # Initialize Pico connection
    pico = picod.pico()
    if not pico.connected:
        print("Failed to connect to Pico")
        exit()
    
    try:
        while True:
            # Both servos clockwise
            pw = CENTER_PW + (SPEED * MAX_DEVIATION)
            pico.tx_servo(GPIO_1, pw)
            pico.tx_servo(GPIO_2, pw)
            time.sleep(2)
            
            # Both servos stop
            pico.tx_servo(GPIO_1, CENTER_PW)
            pico.tx_servo(GPIO_2, CENTER_PW)
            time.sleep(1)
            
            # Both servos counterclockwise
            pw = CENTER_PW + (-SPEED * MAX_DEVIATION)
            pico.tx_servo(GPIO_1, pw)
            pico.tx_servo(GPIO_2, pw)
            time.sleep(2)
            
            # Both servos stop
            pico.tx_servo(GPIO_1, CENTER_PW)
            pico.tx_servo(GPIO_2, CENTER_PW)
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Clean shutdown
        pico.tx_servo(GPIO_1, 0)
        pico.tx_servo(GPIO_2, 0)
        pico.close()
        print("\nProgram terminated by user")

if __name__ == "__main__":
    main()