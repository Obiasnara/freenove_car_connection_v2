import time
import smbus
import threading

from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface


class Battery(MQTT_Module_Interface):
    def __init__(self, comm_handler):
        # Get I2C bus
        self.bus = smbus.SMBus(1)

        # I2C address of the device
        self.ADDRESS = 0x48

        # PCF8591 Command
        self.PCF8591_CMD = 0x40  # Command

        # ADS7830 Command 
        self.ADS7830_CMD = 0x84  # Single-Ended Inputs

        for i in range(3):
            aa = self.bus.read_byte_data(self.ADDRESS, 0xf4)
            if aa < 150:
                self.Index = "PCF8591"
            else:
                self.Index = "ADS7830"

         # We need to create a MQTTHandler object to subscribe to the topic "MotorProducer"
        self.comm_handler = comm_handler
        self.sender = "measurement_value/get_Measurement_Value_Battery_Values"

        self.Left_IDR_temp = 0
        self.Right_IDR_temp = 0
        self.Power_temp = 0
        self.getMessage()

    def getMessage(self):
        def message_loop():  # This function will run in its own thread
            while True:
                Left_IDR = self.recvADC(0)
                Right_IDR = self.recvADC(1)
                Power = self.recvADC(2) * 3
                if Left_IDR != self.Left_IDR_temp or Right_IDR != self.Right_IDR_temp or Power != self.Power_temp:
                    self.Left_IDR_temp = Left_IDR
                    self.Right_IDR_temp = Right_IDR
                    self.Power_temp = Power
                    print("Left_IDR: ", Left_IDR, "Right_IDR: ", Right_IDR, "Power: ", Power)
                    self.comm_handler.publish(self.sender, str(Left_IDR) + "_" + str(Right_IDR) + "_" + str(Power))
                time.sleep(1)  # Sleep within this thread only

        print("Battery Module is running")
        thread = threading.Thread(target=message_loop)
        thread.start()  # Start the thread

    def on_message(self, client, userdata, message):
        pass

    def destroy(self):
        self.i2cClose()
        self.mqtt_handler.stop()

    def analogReadPCF8591(self, chn):  # PCF8591 read ADC value,chn:0,1,2,3
        value = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(9):
            value[i] = self.bus.read_byte_data(self.ADDRESS, self.PCF8591_CMD + chn)
        value = sorted(value)
        return value[4]

    def analogWritePCF8591(self, value):  # PCF8591 write DAC value
        self.bus.write_byte_data(self.ADDRESS, cmd, value)

    def recvPCF8591(self, channel):  # PCF8591 write DAC value
        while (1):
            value1 = self.analogReadPCF8591(channel)  # read the ADC value of channel 0,1,2,
            value2 = self.analogReadPCF8591(channel)
            if value1 == value2:
                break;
        voltage = value1 / 256.0 * 3.3  # calculate the voltage value
        voltage = round(voltage, 2)
        return voltage

    def recvADS7830(self, channel):
        """Select the Command data from the given provided value above"""
        COMMAND_SET = self.ADS7830_CMD | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
        self.bus.write_byte(self.ADDRESS, COMMAND_SET)
        while (1):
            value1 = self.bus.read_byte(self.ADDRESS)
            value2 = self.bus.read_byte(self.ADDRESS)
            if value1 == value2:
                break;
        voltage = value1 / 255.0 * 3.3  # calculate the voltage value
        voltage = round(voltage, 2)
        return voltage

    def recvADC(self, channel):
        if self.Index == "PCF8591":
            data = self.recvPCF8591(channel)
        elif self.Index == "ADS7830":
            data = self.recvADS7830(channel)
        return data

    def i2cClose(self):
        self.bus.close()