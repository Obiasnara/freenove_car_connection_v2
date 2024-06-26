import InitPythonPath as InitPythonPath

from Handlers.MQTT_Handler import MQTTHandler
from ENGINE.MQTT_Motor_Module import Motor
from BATTERY.MQTT_Battery_Module import Battery
from ULTRASONIC.MQTT_Ultrasonic_Module import Ultrasonic
from CPU.MQTT_CPU_Module import CPU

MQTT_BROKER_ADDRESS = "157.245.38.231"
mqtt_handler = MQTTHandler(MQTT_BROKER_ADDRESS, client_id="car_motor_module")
motor = Motor(mqtt_handler)
battery = Battery(mqtt_handler)
ultrasonic = Ultrasonic(mqtt_handler)
cpu = CPU(mqtt_handler)

def loop():
    while True:
        pass

def destroy():
    motor.destroy()
    battery.destroy()
    ultrasonic.destroy()
    cpu.destroy()

if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
