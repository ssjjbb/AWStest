
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
from datetime import datetime
import json
import argparse
from grove.adc import ADC
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
LED_PIN = 11 #GPIO17
light_sensor = 0 #A0 pin connector in ADC shield

threshold = 800 #Threshold value

class GroveLightSensor:
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
        
    @property
    def light(self):
        value = self.adc.read(self.channel)
        return value

def customShadowCallback_Update(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Update request " + token + " timeout!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("-------------------")
        print("Update request with token: " + token + " accepted!")
        print("brightness: " + str(payloadDict["state"]["desired"]["brightness"]))
        print("-------------------")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")
        
def customShadowCallback_Delete(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Delete request " + token + " timeout!")
    if responseStatus == "accepted":
        print("-------------------")
        print("Delete request with token: " + token + " accepted!")
        print("-------------------\n\n")
    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")
        
# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False, help="Use MQTT over websocket")
parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowUpdater", help="Target ID")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
thingName = args.thingName
clientId = args.clientId

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and Websocket are mutual exclusive. Please pick one.")
    exit(2)

if args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)
    
#Port defaults
if args.useWebsocket and not args.port: #Default to port 443
    port = 443
if not args.useWebsocket and not args.port:
    port = 8883
    
#Logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


#init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
if useWebsocket:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, port)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, port)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
    
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)

#Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

#Create a deviceShadow with persistent subscription
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)

#Delete shadow JSON doc
deviceShadowHandler.shadowDelete(customShadowCallback_Delete, 5)

#Update shadow in a loop
loopCount = 0
sensor = GroveLightSensor(0)
while True:
    brightness = sensor.light
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    JSONPayload = '{"state":{"desired":{"time":"' + str(timestamp) + '","brightness":'+str(brightness) + '}}}'
    print("\n", JSONPayload, "\n")
    print("\n", brightness, "\n")
    deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)
    if brightness > threshold:
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, True) #LED ON
    else:
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, False) #LED OFF
    loopCount = loopCount + 1
    time.sleep(1)








