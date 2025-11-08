# 🌍 Air Pollution Monitoring System (ESP32 + MicroPython)

This project uses *ESP32, **MQ135, and **DHT11* to monitor air quality, temperature, and humidity — built entirely in *Thonny IDE (MicroPython)*.  
The system can also send alerts through *Telegram Bot* when the air quality exceeds a safe threshold.

---

## 🧠 Components Used

- ESP32 Board  
- MQ135 Gas Sensor  
- DHT11 Temperature and Humidity Sensor  
- Breadboard & Jumper Wires  

---

## ⚙ Circuit Connections

| Sensor | Pin | ESP32 Pin |
|--------|-----|-----------|
| MQ135 | AO | GPIO 34 |
| DHT11 | OUT | GPIO 4 |
| VCC | 3.3V | 3.3V |
| GND | GND | GND |

---

## 💻 How to Run (Thonny IDE)

1. Open *Thonny IDE*.
2. Select Interpreter → *MicroPython (ESP32)*.
3. Connect your ESP32 board via USB.
4. Open and upload all files:
   - overall.py
   - display.py
   - mq135.py
5. Edit Wi-Fi and E-mail credentials in overall.py.
6. Click *Run* or press *F5*.
7. Observe readings in the *Shell*.

---

## 📡 Output Example
Temperature: 27.4 °C
Humidity: 62 %
Air Quality: 178 (Moderate)
Wi-Fi Connected!
E-mail Sent: Air quality alert!
