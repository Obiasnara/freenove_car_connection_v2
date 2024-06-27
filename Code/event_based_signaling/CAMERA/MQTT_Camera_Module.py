from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

rtmp_url = "rtmp://157.245.38.231/live/stream1"
class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler): 
        self.camera = Picamera2()
        self.video_config = self.camera.create_video_configuration()
        self.camera.configure(self.video_config)

        self.output = FfmpegOutput(f"-f flv {rtmp_url}")  
        self.encoder = H264Encoder()
        self.start_streaming()

    def start_streaming(self):
        self.picam2.start_recording(self.encoder, self.output) 

    def stop_streaming(self):
        self.picam2.stop_recording()

    def on_message(self, client, userdata, message):
        if message.topic == self.mqtt_topic:
            self.camera.take_picture()
            self.camera.send_picture()
            self.camera.delete_picture()

    def getMessages(self):
        pass
    
    def destroy(self):
        pass