import InitPythonPath
import threading
import json
from MQTT_Handler import MQTTHandler
from car_utilities.Motor import Motor

MQTT_BROKER_ADDRESS = "157.245.38.231"
mqtt_handler = MQTTHandler(MQTT_BROKER_ADDRESS, client_id="my_client")

LeftUpperMotorSpeed = 0
RightUpperMotorSpeed = 0
LeftLowerMotorSpeed = 0
RightLowerMotorSpeed = 0

def on_message(client, userdata, message):
    global LeftUpperMotorSpeed, RightUpperMotorSpeed, LeftLowerMotorSpeed, RightLowerMotorSpeed
    data = json.loads(message.payload)
    LeftUpperMotorSpeed = data["LeftUpperMotorSpeed"]
    RightUpperMotorSpeed = data["RightUpperMotorSpeed"]
    LeftLowerMotorSpeed = data["LeftLowerMotorSpeed"]
    RightLowerMotorSpeed = data["RightLowerMotorSpeed"]
    motor.setMotorModel(LeftUpperMotorSpeed, RightUpperMotorSpeed, LeftLowerMotorSpeed, RightLowerMotorSpeed)

def loop():
    global LeftUpperMotorSpeed, RightUpperMotorSpeed, LeftLowerMotorSpeed, RightLowerMotorSpeed
    i=0;    
    motor = Motor()
    mqtt_handler.subscribe("MotorProducer")        
    mqtt_handler.client.on_message = on_message
    while True:
        LeftUpperMotorSpeed, RightUpperMotorSpeed, LeftLowerMotorSpeed, RightLowerMotorSpeed = motor.duty_range(LeftUpperMotorSpeed, RightUpperMotorSpeed, LeftLowerMotorSpeed, RightLowerMotorSpeed)
        data = {
            "LeftUpperMotorSpeed": f"{LeftUpperMotorSpeed}",
            "RightUpperMotorSpeed": f"{RightUpperMotorSpeed}",
            "LeftLowerMotorSpeed": f"{LeftLowerMotorSpeed}",
            "RightLowerMotorSpeed": f"{RightLowerMotorSpeed}",
        }
        mqtt_handler.publish("MotorClient", data)
        mqtt_handler.wait_for_publish()
        # Add break caracter to stop the loop

def destroy():
    mqtt_handler.stop()

if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()