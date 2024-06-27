from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput, FileOutput
import subprocess
import threading
import time
from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

RTMP_SERVER_IP = "157.245.38.231"  
STREAM_NAME = "stream1"

class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler=None): 
        self.picam2 = Picamera2()
        video_config = self.picam2.create_video_configuration(main={"size": (640, 480)})
        self.picam2.configure(video_config) 
        self.encoder = H264Encoder(bitrate=1000000, repeat=True)  
        #self.output = FfmpegOutput(f'rtmp://{RTMP_SERVER_IP}/live/{STREAM_NAME}')
        #self.output = FfmpegOutput("test.mp4", audio=False)
        self.output = FileOutput('testazdazd.h264')
        self.streaming_thread = None 

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