import RPi.GPIO as GPIO
import time
import threading

from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

class Ultrasonic(MQTT_Module_Interface):
    def __init__(self, comm_handler):
        GPIO.cleanup()  # Clean up the GPIO pins
        GPIO.setwarnings(False)
        self.trigger_pin = 27
        self.echo_pin = 22
        self.MAX_DISTANCE = 300  # define the maximum measuring distance, unit: cm
        self.timeOut = self.MAX_DISTANCE * 60  # calculate timeout according to the maximum measuring distance
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

        # Check GPIO pins
        print("Trigger pin: ", self.trigger_pin)
        print("Echo pin: ", self.echo_pin)

        # We need to create a MQTTHandler object to subscribe to the topic "MotorProducer"
        self.comm_handler = comm_handler
        self.sender = "Submodel1_Operation4"
        self.distance_temp = []
        self.getMessage()

    def getMessage(self):
        def message_loop():  # Function to run in a separate thread
            while True:
                print("Getting distance")
                thread = threading.Thread(target=self.get_distance)  
                thread.start()  # Launch the thread
                distance = thread.join()  # Wait for the thread to finish
                if distance != self.distance_temp:
                    self.distance_temp = distance
                    self.comm_handler.publish(self.sender, str(distance))
                time.sleep(1)  # Sleep only within this thread
        
        thread = threading.Thread(target=message_loop)  
        thread.start()  # Launch the thread
    
    def on_message(self, client, userdata, message):
        pass

    def destroy(self):
        self.i2cClose()
        self.mqtt_handler.stop()
        GPIO.cleanup()  # Clean up the GPIO pins

    def pulseIn(self, pin, level, timeOut):  # obtain pulse time of a pin under timeOut
        t0 = time.time()
        while (GPIO.input(pin) != level):
            if ((time.time() - t0) > timeOut * 0.000001):
                return 0;
        t0 = time.time()
        while (GPIO.input(pin) == level):
            if ((time.time() - t0) > timeOut * 0.000001):
                return 0;
        pulseTime = (time.time() - t0) * 1000000
        return pulseTime

    def get_distance(self):
        distances = []
        for _ in range(10):  # Increase sample size
            GPIO.output(self.trigger_pin, GPIO.HIGH)
            time.sleep(0.00001)  # Initial delay
            GPIO.output(self.trigger_pin, GPIO.LOW)
            print("Triggered")
            while GPIO.input(self.echo_pin) == GPIO.LOW:  # Wait for echo start
                pass
            print("Echo started")
            startTime = time.time()

            while GPIO.input(self.echo_pin) == GPIO.HIGH:  # Wait for echo end
                if time.time() - startTime > self.timeOut * 0.000001:
                    return 0  # Timeout
            print("Echo ended")
            pulseTime = (time.time() - startTime) * 1000000
            distances.append(pulseTime * 340.0 / 2.0 / 10000.0)

        distances = sorted(distances)
        print(distances)
        return int(distances[2:-2])  # Median after removing outliers


    