from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

picam2 = Picamera2()
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

# Replace 'your_rtmp_url' with your actual RTMP server URL
rtmp_url = "rtmp://157.245.38.231/live/stream1"

# Configure FFmpeg output for RTMP streaming
output = FfmpegOutput(f"-f flv {rtmp_url}")  

encoder = H264Encoder()
picam2.start_recording(encoder, output)

# Keep the stream running (you'll need to handle stopping in your application)
try:
    while True:
        pass
except KeyboardInterrupt:
    picam2.stop_recording()