from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
import subprocess
import threading
import time
from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface


ffmpeg_cmd = [
        'ffmpeg',  # FFmpeg executable
        '-hide_banner',  # Hide FFmpeg banner
        '-loglevel', 'error',  # Suppress non-error FFmpeg logs
        '-f', 'rawvideo',  # Input format: raw video
        '-pix_fmt', 'bgr24',  # Pixel format: 24-bit BGR
        '-s', '{}x{}'.format(int(cap.get(3)), int(cap.get(4))),  # Input video resolution
        '-r', '30',  # Input frame rate: 60 frames per second
        '-i', '-',  # Read input from stdin
        '-c:v', 'libx264',  # Video codec: H.264 with libx264 encoder
        '-pix_fmt', 'yuv420p',  # Pixel format for output: YUV420p
        '-preset', 'ultrafast',  # Encoding preset: ultrafast for speed
        '-tune', 'zerolatency',  # Tune settings for low-latency streaming
        '-movflags', '+faststart',  # Enable fast start for video playback
        '-crf', '20',  # Constant Rate Factor for video quality
        '-g', '1',  # Keyframe interval
        '-b:v', '5M',  # Target video bitrate: 1 Mbps
        '-f', 'flv',  # Output format: FLV (Flash Video)
        '-an',  # Disable audio encoding
        '-c:a', 'aac',  # Audio codec: AAC
        '-bufsize', '1M',  # Buffer size for video encoding
        '-maxrate', '5M',  # Maximum video bitrate: 1 Mbps
        'rtmp://{}/live/{}'.format(RTMP_SERVER_IP, stream_name)  # RTMP server URL
    ]

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
            'ffmpeg',  # FFmpeg executable
            '-hide_banner',  # Hide FFmpeg banner
            '-loglevel', 'error',  # Suppress non-error FFmpeg logs
            '-f', 'rawvideo',  # Input format: raw video
            '-pix_fmt', 'bgr24',  # Pixel format: 24-bit BGR
            '-r', '30',  # Input frame rate: 60 frames per second
            '-i', '-',  # Read input from stdin
            '-c:v', 'libx264',  # Video codec: H.264 with libx264 encoder
            '-pix_fmt', 'yuv420p',  # Pixel format for output: YUV420p
            '-preset', 'ultrafast',  # Encoding preset: ultrafast for speed
            '-tune', 'zerolatency',  # Tune settings for low-latency streaming
            '-movflags', '+faststart',  # Enable fast start for video playback
            '-crf', '20',  # Constant Rate Factor for video quality
            '-g', '1',  # Keyframe interval
            '-b:v', '5M',  # Target video bitrate: 1 Mbps
            '-f', 'flv',  # Output format: FLV (Flash Video)
            '-an',  # Disable audio encoding
            '-c:a', 'aac',  # Audio codec: AAC
            '-bufsize', '1M',  # Buffer size for video encoding
            '-maxrate', '5M',  # Maximum video bitrate: 1 Mbps
            'rtmp://{}/live/{}'.format(RTMP_SERVER_IP, stream_name)  # RTMP server URL
        ]

        self.encoder.output = self.ffmpeg_output
        self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
        self.picam2.start_recording(self.encoder, self.ffmpeg_process.stdin)  

        self.streaming_thread = threading.Thread(target=self._monitor_streaming)
        self.streaming_thread.start()

    def _monitor_streaming(self):
        while self.picam2.is_recording:
            time.sleep(0.1)  # Periodic check, adjust as needed

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