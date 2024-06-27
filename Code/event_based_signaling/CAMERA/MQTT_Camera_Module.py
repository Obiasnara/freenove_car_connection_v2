from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
from picamera2 import Picamera2
import time

from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface


import subprocess
from picamera2 import Picamera2, Preview


# FFmpeg Command
rtmp_url = "rtmp://your-server-address/live/your-stream-key"  
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-f", "h264", 
    "-i", "-",  
    "-c:v", "libx264",  
    "-preset", "ultrafast", 
    "-tune", "zerolatency", 
    "-f", "flv", 
    rtmp_url
]


# ffmpeg_cmd = [
#         'ffmpeg',  # FFmpeg executable
#         '-hide_banner',  # Hide FFmpeg banner
#         '-loglevel', 'error',  # Suppress non-error FFmpeg logs
#         '-f', 'rawvideo',  # Input format: raw video
#         '-pix_fmt', 'bgr24',  # Pixel format: 24-bit BGR
#         '-s', '{}x{}'.format(int(cap.get(3)), int(cap.get(4))),  # Input video resolution
#         '-r', '30',  # Input frame rate: 60 frames per second
#         '-i', '-',  # Read input from stdin
#         '-c:v', 'libx264',  # Video codec: H.264 with libx264 encoder
#         '-pix_fmt', 'yuv420p',  # Pixel format for output: YUV420p
#         '-preset', 'ultrafast',  # Encoding preset: ultrafast for speed
#         '-tune', 'zerolatency',  # Tune settings for low-latency streaming
#         '-movflags', '+faststart',  # Enable fast start for video playback
#         '-crf', '20',  # Constant Rate Factor for video quality
#         '-g', '1',  # Keyframe interval
#         '-b:v', '5M',  # Target video bitrate: 1 Mbps
#         '-f', 'flv',  # Output format: FLV (Flash Video)
#         '-an',  # Disable audio encoding
#         '-c:a', 'aac',  # Audio codec: AAC
#         '-bufsize', '1M',  # Buffer size for video encoding
#         '-maxrate', '5M',  # Maximum video bitrate: 1 Mbps
#         'rtmp://{}/live/{}'.format(RTMP_SERVER_IP, stream_name)  # RTMP server URL
#     ]

class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler):
        self.comm_handler = comm_handler
        self.sender = "Submodel1_Operation6"

        # Camera Setup
        self.picam2 = Picamera2()
        self.picam2.start_preview(Preview.NULL)  # Start preview without displaying (for efficiency)
        self.video_config = self.picam2.create_video_configuration(main={"size": (1280, 720)})  # Adjust resolution
        self.picam2.configure(self.video_config)
        # Start Streaming
        self.picam2.start_recording(
            FfmpegEncoder(),
            subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE).stdin
        )


        # initialize the camera and grab a reference to the raw camera capture
        # self.camera = Picamera2()
        # self.camera.configure(self.camera.create_video_configuration())
        # self.encoder = H264Encoder(bitrate=170000, repeat=True, iperiod=15)
        # stream_name = "stream1"
        # RTMP_SERVER_IP = "157.245.38.231"
        # self.ffmpeg_output = FfmpegOutput(output_filename='-f rtmp://{}/live/{}'.format(RTMP_SERVER_IP, stream_name))
        # self.encoder.output = self.ffmpeg_output
        # self.camera.start_recording(self.encoder, "test.h264", quality=Quality.VERY_LOW)
        # time.sleep(30)
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