import RPi.GPIO as GPIO
import time
import speedtest

# GPIO to LCD mapping
LCD_RS = 26  # Pi pin 37
LCD_E = 19  # Pi pin 35
LCD_D4 = 13  # Pi pin 33
LCD_D5 = 6  # Pi pin 31
LCD_D6 = 5  # Pi pin 29
LCD_D7 = 11  # Pi pin 23

# Device constants
LCD_CHR = True  # Character mode
LCD_CMD = False  # Command mode
LCD_CHARS = 16  # Characters per line (16 max)
LCD_LINE_1 = 0x80  # LCD memory location for 1st line
LCD_LINE_2 = 0xC0  # LCD memory location for 2nd line

# Initialize LCD
def lcd_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # Set GPIO's to output mode
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_D4, GPIO.OUT)
    GPIO.setup(LCD_D5, GPIO.OUT)
    GPIO.setup(LCD_D6, GPIO.OUT)
    GPIO.setup(LCD_D7, GPIO.OUT)
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(0.0005)  # Delay to allow commands to process

# Send byte to data pins
def lcd_byte(bits, mode):
    GPIO.output(LCD_RS, mode)  # RS

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

# Toggle the enable pin
def lcd_toggle_enable():
    time.sleep(0.0005)
    GPIO.output(LCD_E, True)
    time.sleep(0.0005)
    GPIO.output(LCD_E, False)
    time.sleep(0.0005)

# Print text to LCD
def lcd_string(message, line):
    message = message.ljust(LCD_CHARS, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_CHARS):
        lcd_byte(ord(message[i]), LCD_CHR)

# Run speed test
def run_speed_test():
    st = speedtest.Speedtest()
    st.get_best_server()
    ping = st.results.ping
    download_speed = st.download() / 10**6  # Convert to Mbps
    upload_speed = st.upload() / 10**6  # Convert to Mbps
    return ping, download_speed, upload_speed

# Display speed test results on LCD
def display_speed_test_results(ping, download_speed, upload_speed, time_since_last_test):
    lcd_string(f"Ping: {ping:.2f} ms", LCD_LINE_1)
    lcd_string(f"Download: {download_speed:.2f} Mbps", LCD_LINE_2)
    time.sleep(3)
    lcd_string(f"Upload: {upload_speed:.2f} Mbps", LCD_LINE_1)
    lcd_string(f"Time since last: {time_since_last_test} sec", LCD_LINE_2)

# Main program
if __name__ == "__main__":
    try:
        # Initialize LCD
        lcd_init()
        
        # Main loop
        while True:
            start_time = time.time()

            # Run speed test
            ping, download_speed, upload_speed = run_speed_test()

            # Calculate time since last test
            time_since_last_test = int(time.time() - start_time)

            # Display results on LCD
            display_speed_test_results(ping, download_speed, upload_speed, time_since_last_test)

            # Wait for 5 minutes
            time.sleep(300)

    except KeyboardInterrupt:
        pass

    finally:
        lcd_byte(0x01, LCD_CMD)
        lcd_string("Goodbye!", LCD_LINE_1)
        GPIO.cleanup()