#LDR test reader

import time
import grovepi
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
LED_PIN = 11 #GPIO17
light_sensor = 0 #A0 pinni grove ADC boardilla

treshold = 800 #Treshold value ledin syttymiselle

grovepi.pinMode(light_sensor, "INPUT")

while True:
    try:
        sensor_value = grovepi.analogRead(light_sensor)
        
        resistance = (float)(1023 - sensor_value) * 10 / sensor_value
        
        if resistance > treshold:
            GPIO.setup(PIN, GPIO.OUT)
            GPIO.output(PIN, False) #LED pois päältä
        else:
            GPIO.setup(PIN, GPIO.OUT)
            GPIO.output(PIN, True) #LED päälle
            
        print("LDR value = %d resistanssi = %.2f" %(sensor_value, resistance))
        time.sleep(.5)
    except IOError:
        print("Error")

