from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
import subprocess
import threading
import time
from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

RTMP_SERVER_IP = "157.245.38.231"  
STREAM_NAME = "stream1"

class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler):  # Optional comm_handler for future use
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 480)}))  # Set desired resolution
        self.encoder = H264Encoder(bitrate=1000000, repeat=True)  
        self.ffmpeg_output = FfmpegOutput('rtmp://{}/live/{}'.format(RTMP_SERVER_IP, STREAM_NAME))  
        self.streaming_thread = None 
        self.start_streaming() 

    def start_streaming(self):
        ffmpeg_cmd = [
            'ffmpeg',
            '-hide_banner', '-loglevel', 'error',
            '-f', 'h264',  # Input format is H.264 
            '-i', '-',     # Input from stdin (pipe)
            '-c:v', 'copy',  # No re-encoding for speed (if needed you can add -c:v libx264)
            '-f', 'flv',  # Output format is FLV (required for RTMP)
            'rtmp://{}/live/{}'.format(RTMP_SERVER_IP, STREAM_NAME)
        ]

        self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
        self.picam2.start_recording(self.encoder, self.ffmpeg_process.stdin)  

    def stop_streaming(self):
        self.picam2.stop_recording()
        if self.ffmpeg_process:
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait() 
        if self.streaming_thread:
            self.streaming_thread.join() 

    def on_message(self, client, userdata, message):
        if message.topic == self.mqtt_topic:
            self.camera.take_picture()
            self.camera.send_picture()
            self.camera.delete_picture()

    def getMessages(self):
        pass
    
    def destroy(self):
        pass