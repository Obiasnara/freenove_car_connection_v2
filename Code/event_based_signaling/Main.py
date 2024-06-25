import InitPythonPath

from MQTT_Handler import MQTTHandler
from ENGINE.MQTT_Motor_Module import Motor

MQTT_BROKER_ADDRESS = "157.245.38.231"
mqtt_handler = MQTTHandler(MQTT_BROKER_ADDRESS, client_id="car_motor_module")
motor = Motor(mqtt_handler)

def loop():
    while True:
        pass

def destroy():
    motor.setMotorModel(0, 0, 0, 0)
    motor.mqtt_handler.stop()

if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
