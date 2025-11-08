from machine import Pin, ADC
from time import sleep

# Configure the ADC pin (GPIO34)
mq135 = ADC(Pin(26))
mq135.atten(ADC.ATTN_11DB)  # Full range: 0 - 3.3V
mq135.width(ADC.WIDTH_12BIT)  # Resolution: 12-bit (0 - 4095)

print("MQ135 Sensor Test Starting...\n")

while True:
    analog_value = mq135.read()
    
    # Approximate air quality level (for testing only)
    if analog_value < 1000:
        quality = "Fresh Air"
    elif analog_value < 2000:
        quality = "Normal Air"
    elif analog_value < 3000:
        quality = "Poor Air"
    else:
        quality = "Polluted Air"
    
    print("Analog Value:", analog_value, "| Air Quality:", quality)
    sleep(1)
