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
            rtmp_url
        ]
        self.output = FfmpegOutput(ffmpeg_cmd)
        #self.output = FfmpegOutput(f"-f flv {rtmp_url}")  
        self.encoder = H264Encoder()
        self.start_streaming()

    def start_streaming(self):
        self.camera.start_recording(self.encoder, self.output) 

    def stop_streaming(self):
        self.camera.stop_recording()

    def on_message(self, client, userdata, message):
        if message.topic == self.mqtt_topic:
            self.camera.take_picture()
            self.camera.send_picture()
            self.camera.delete_picture()

    def getMessages(self):
        pass
    
    def destroy(self):
        pass