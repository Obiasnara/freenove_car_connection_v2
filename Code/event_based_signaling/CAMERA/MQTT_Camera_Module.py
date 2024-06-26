from picamera2.encoders import H264Encoder, Quality
from picamera2 import Picamera2
import time

from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler):
        self.comm_handler = comm_handler
        self.sender = "Submodel1_Operation6"

        # initialize the camera and grab a reference to the raw camera capture
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_video_configuration())
        self.encoder = H264Encoder(bitrate=17000000, repeat=True, iperiod=15)

        self.camera.start_recording(self.encoder, 'test.h264', quality=Quality.VERY_LOW)
        time.sleep(10)
        self.camera.stop_recording()
        self.camera.close()

    def on_message(self, client, userdata, message):
        if message.topic == self.mqtt_topic:
            self.camera.take_picture()
            self.camera.send_picture()
            self.camera.delete_picture()

    def getMessages(self):
        pass
    
    def destroy(self):
        pass