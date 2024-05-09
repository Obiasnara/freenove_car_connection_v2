import InitPythonPath
import threading
import json
from MQTT_Motor_Module import Motor

def loop():
    motor = Motor()
    
    while True:
        pass

def destroy():
    mqtt_handler.stop()

if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()