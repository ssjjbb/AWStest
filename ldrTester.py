#LDR test reader
#Lights LED up depending how dark it is around the sensor
#Used in testing only
import time
import grovepi
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
LED_PIN = 11 #GPIO17
light_sensor = 0 #A0 Pin on ADC shield

treshold = 800 #Treshold value for LED to light up

grovepi.pinMode(light_sensor, "INPUT")

while True:
    try:
        sensor_value = grovepi.analogRead(light_sensor)
        
        resistance = (float)(1023 - sensor_value) * 10 / sensor_value
        
        if resistance > treshold:
            GPIO.setup(PIN, GPIO.OUT)
            GPIO.output(PIN, False) #LED off
        else:
            GPIO.setup(PIN, GPIO.OUT)
            GPIO.output(PIN, True) #LED on
            
        print("LDR value = %d resistanssi = %.2f" %(sensor_value, resistance))
        time.sleep(.5)
    except IOError:
        print("Error")

