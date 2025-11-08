from machine import Pin, I2C, ADC
import dht
import time
import ssd1306
import math
import network
import urequests
import json

# =========================================================
# --- WIFI & EMAIL CONFIGURATION (UPDATE THESE) ---
# =========================================================

WIFI_SSID = "Vikky_Realme"
WIFI_PASSWORD = "vikky7671"

# Using Formspree.io for email (FREE & EASY)
FORMSPREE_URL = "https://formspree.io/f/xanpaaav"

SENDER_EMAIL = "mvaradarajulu25@gmail.com"
RECIPIENT_EMAIL = "jvikky86@gmail.com"  # SAME EMAIL - sends to yourself

# Email sending interval (in seconds)
EMAIL_SEND_INTERVAL = 30  # Send email every 30 seconds

# =========================================================
# --- SENSOR CONFIGURATION (UPDATE THESE VALUES) ---
# =========================================================

R0_CALIBRATION_COMPLETE = True 

# --- Pin Assignments ---
I2C_SDA_PIN = 21
I2C_SCL_PIN = 22
DHT_PIN = 4
MQ135_PIN = 36

# --- MQ-135 Calibration Constants ---
R0_CLEAN_AIR = 10.0

# Fixed Constants
OLED_WIDTH = 128
OLED_HEIGHT = 64
I2C_ADDR = 0x3c 
VOLTAGE_RESOLUTION = 3.3
ADC_MAX = 4095
R_LOAD = 10.0 
R0_CLEAN_AIR_RATIO = 2.66 
A = 110.0
B = -2.65

# =========================================================
# --- INITIALIZATION ---
# =========================================================

# DHT Sensor
dht_sensor = dht.DHT11(Pin(DHT_PIN))

# MQ-135 ADC
mq135_adc = ADC(Pin(MQ135_PIN))
mq135_adc.atten(ADC.ATTN_11DB) 
mq135_adc.width(ADC.WIDTH_12BIT) 

# OLED Display
try:
    i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
    oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=I2C_ADDR)
except Exception as e:
    print(f"I2C or OLED init failed: {e}")
    time.sleep(5)

# WiFi
wlan = network.WLAN(network.STA_IF)

# =========================================================
# --- WIFI CONNECTION FUNCTION ---
# =========================================================

def connect_wifi():
    """Connect to WiFi network."""
    try:
        wlan.active(True)
        time.sleep(1)
        
        if not wlan.isconnected():
            print(f"Connecting to WiFi: {WIFI_SSID}")
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            
            timeout = 20
            while not wlan.isconnected() and timeout > 0:
                print(".", end="")
                time.sleep(1)
                timeout -= 1
            
            if wlan.isconnected():
                print("\nWiFi Connected!")
                print(f"IP: {wlan.ifconfig()[0]}")
                return True
            else:
                print("\nFailed to connect to WiFi!")
                return False
        else:
            print("Already connected to WiFi")
            return True
    except Exception as e:
        print(f"WiFi Error: {e}")
        return False

# =========================================================
# --- EMAIL SENDING FUNCTION (SIMPLER METHOD) ---
# =========================================================

def send_email(temp, hum, ppm, mq_status):
    """Send sensor data via email using Formspree (RECOMMENDED)."""
    try:
        print("Sending email via web service...")
        
        # Prepare email data
        email_data = {
            "email": SENDER_EMAIL,
            "message": f"""Air Quality Report

Temperature: {temp:.1f} C
Humidity: {hum:.1f} %
CO2 Equivalent: {int(ppm)} PPM
Air Quality Status: {mq_status}

Device: ESP32 Air Monitor
Time: {time.time()}
"""
        }
        
        # Send via HTTP POST
        response = urequests.post(FORMSPREE_URL, json=email_data)
        
        if response.status_code == 200:
            print("✅ Email sent successfully!")
            response.close()
            return True
        else:
            print(f"Email failed: {response.status_code}")
            response.close()
            return False
            
    except Exception as e:
        print(f"Email error: {e}")
        return False

# =========================================================
# --- SENSOR PROCESSING FUNCTIONS ---
# =========================================================

def calculate_Rs(raw_adc):
    """Calculates Sensor Resistance (Rs) in kOhms."""
    voltage = raw_adc * (VOLTAGE_RESOLUTION / ADC_MAX)
    
    if voltage > 0:
        Rs = R_LOAD * ((VOLTAGE_RESOLUTION / voltage) - 1)
        return Rs
    return 0.0

def get_mq135_ppm(Rs):
    """Converts Sensor Resistance (Rs) to CO2 equivalent PPM."""
    
    if R0_CLEAN_AIR <= 0 or not R0_CALIBRATION_COMPLETE:
        return 0.0

    Rs_R0 = Rs / R0_CLEAN_AIR 
    ppm = A * math.pow(Rs_R0, B)
    
    return ppm

def classify_air_quality(ppm):
    """Classifies air quality based on CO2 equivalent PPM standards."""
    if ppm <= 800:
        return "GOOD"
    elif ppm <= 1500:
        return "MODERATE"
    else:
        return "BAD"

# =========================================================
# --- DISPLAY FUNCTIONS ---
# =========================================================

def display_readings(temp, hum, ppm, mq_status, wifi_status):
    """Normal operational display."""
    oled.fill(0) 
    oled.text("--- Air Monitor ---", 0, 0)
    oled.text(f"Temp: {temp:.1f} C", 0, 15)
    oled.text(f"Hum: {hum:.1f} %", 0, 30)
    oled.text("CO2 Eq:", 0, 45)
    oled.text(f"{int(ppm)} PPM", 55, 45)
    oled.text(f"{mq_status} W:{wifi_status}", 0, 55)
    oled.show()

def display_wifi_connecting():
    """Display WiFi connection status."""
    oled.fill(0)
    oled.text("Connecting WiFi...", 0, 25)
    oled.text(WIFI_SSID[:16], 0, 40)
    oled.show()

def display_sending_email():
    """Display email sending status."""
    oled.fill(0)
    oled.text("Sending Email...", 0, 25)
    oled.show()

# =========================================================
# --- MAIN LOOP ---
# =========================================================

if R0_CALIBRATION_COMPLETE:
    print(f"Starting Air Monitor with WiFi & Email.")
    
    # Connect to WiFi
    display_wifi_connecting()
    time.sleep(2)
    wifi_connected = connect_wifi()
    
    last_email_time = 0
    
    while True:
        try:
            temp = 0.0
            hum = 0.0
            
            # 1. Read DHT11 Sensor
            try:
                dht_sensor.measure()
                temp = dht_sensor.temperature()
                hum = dht_sensor.humidity()
            except OSError:
                pass 

            # 2. Read MQ-135 Sensor, Calculate PPM, and Classify
            mq_raw = mq135_adc.read()
            Rs = calculate_Rs(mq_raw)
            ppm = get_mq135_ppm(Rs)
            mq_status = classify_air_quality(ppm)
            
            # Determine WiFi status display
            wifi_status = "ON" if wlan.isconnected() else "OFF"
            
            # 3. Display on OLED
            display_readings(temp, hum, ppm, mq_status, wifi_status)

            # 4. Print to Console
            print(f"T={temp:.1f}C, H={hum:.1f}%, Rs={Rs:.2f} kOhm, PPM={int(ppm)}, Status={mq_status}, WiFi={wifi_status}")
            
            # 5. Send Email at intervals
            current_time = time.time()
            if (current_time - last_email_time) >= EMAIL_SEND_INTERVAL and wlan.isconnected():
                display_sending_email()
                print("Sending email...")
                if send_email(temp, hum, ppm, mq_status):
                    print("Email sent!")
                    last_email_time = current_time
                else:
                    print("Failed to send email")
                time.sleep(2)
            
            time.sleep(5)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)