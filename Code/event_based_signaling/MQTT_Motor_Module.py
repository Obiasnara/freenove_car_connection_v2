from car_utilities.PCA9685 import *
import json
import time

class Motor:
    def __init__(self, mqtt_handler):
        self.pwm = PCA9685(0x40, debug=True)
        self.pwm.setPWMFreq(50)

        self.FrontRightWheelDuty = 0
        self.FrontLeftWheelDuty = 0
        self.BackRightWheelDuty = 0
        self.BackLeftWheelDuty = 0
        data = {
            "LeftUpperMotorSpeed": 0,
            "RightUpperMotorSpeed": 0,
            "LeftLowerMotorSpeed": 0,
            "RightLowerMotorSpeed": 0
        }
        # We need to create a MQTTHandler object to subscribe to the topic "MotorProducer"
        self.mqtt_handler = mqtt_handler
        self.mqtt_handler.subscribe("MotorProducer")        
        self.mqtt_handler.client.on_message = self.on_message
        self.sendMessage()

    def on_message(self, client, userdata, message):
        data = json.loads(message.payload)
        print(data)
        print("Recieved")
        self.setMotorModel(data["LeftUpperMotorSpeed"], data["LeftLowerMotorSpeed"], data["RightUpperMotorSpeed"], data["RightLowerMotorSpeed"])

    def duty_range(self, duty1, duty2, duty3, duty4):
        if duty1 > 4095:
            duty1 = 4095
        elif duty1 < -4095:
            duty1 = -4095
        if duty2 > 4095:
            duty2 = 4095
        elif duty2 < -4095:
            duty2 = -4095

        if duty3 > 4095:
            duty3 = 4095
        elif duty3 < -4095:
            duty3 = -4095

        if duty4 > 4095:
            duty4 = 4095
        elif duty4 < -4095:
            duty4 = -4095
        return duty1, duty2, duty3, duty4

    def left_Upper_Wheel(self, duty):
        self.FrontLeftWheelDuty = duty
        if duty > 0:
            self.pwm.setMotorPwm(0, 0)
            self.pwm.setMotorPwm(1, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(1, 0)
            self.pwm.setMotorPwm(0, abs(duty))
        else:
            self.pwm.setMotorPwm(0, 4095)
            self.pwm.setMotorPwm(1, 4095)

    def left_Lower_Wheel(self, duty):
        self.BackLeftWheelDuty = duty
        if duty > 0:
            self.pwm.setMotorPwm(3, 0)
            self.pwm.setMotorPwm(2, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(2, 0)
            self.pwm.setMotorPwm(3, abs(duty))
        else:
            self.pwm.setMotorPwm(2, 4095)
            self.pwm.setMotorPwm(3, 4095)

    def right_Upper_Wheel(self, duty):
        self.FrontRightWheelDuty = duty
        if duty > 0:
            self.pwm.setMotorPwm(6, 0)
            self.pwm.setMotorPwm(7, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(7, 0)
            self.pwm.setMotorPwm(6, abs(duty))
        else:
            self.pwm.setMotorPwm(6, 4095)
            self.pwm.setMotorPwm(7, 4095)

    def right_Lower_Wheel(self, duty):
        self.BackRightWheelDuty = duty
        if duty > 0:
            self.pwm.setMotorPwm(4, 0)
            self.pwm.setMotorPwm(5, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(5, 0)
            self.pwm.setMotorPwm(4, abs(duty))
        else:
            self.pwm.setMotorPwm(4, 4095)
            self.pwm.setMotorPwm(5, 4095)

    def setMotorModel(self, duty1, duty2, duty3, duty4):
        duty1, duty2, duty3, duty4 = self.duty_range(duty1, duty2, duty3, duty4)
        self.left_Upper_Wheel(duty1)
        self.left_Lower_Wheel(duty2)
        self.right_Upper_Wheel(duty3)
        self.right_Lower_Wheel(duty4)
        self.sendMessage()
        print("New duty cycle: ", duty1, duty2, duty3, duty4)


    def sendMessage(self):
        data = {
            "LeftUpperMotorSpeed": self.FrontLeftWheelDuty,
            "RightUpperMotorSpeed": self.FrontRightWheelDuty,
            "LeftLowerMotorSpeed": self.BackLeftWheelDuty,
            "RightLowerMotorSpeed": self.BackRightWheelDuty
        }
        print("Sending message")
        self.mqtt_handler.publish("MotorClient", data)
        print("Sent")


    def getMotorModel(self):
        return self.FrontRightWheelDuty, self.FrontLeftWheelDuty, self.BackRightWheelDuty, self.BackLeftWheelDuty

    def getSpeed(self):
        return self.FrontRightWheelDuty, self.FrontLeftWheelDuty, self.BackRightWheelDuty, self.BackLeftWheelDuty

    def getMotorModel(self):
        return self.FrontRightWheelDuty, self.FrontLeftWheelDuty, self.BackRightWheelDuty, self.BackLeftWheelDuty
