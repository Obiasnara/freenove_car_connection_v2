from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import threading
import time
import fcntl
import struct
import socket
from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

rtmp_url = "rtmp://157.245.38.231/live/stream1"
hls_url = "https://157.245.38.231/hls/stream1.m3u8"
class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler): 
        self.camera = Picamera2()
        self.video_config = self.camera.create_video_configuration()
        self.camera.configure(self.video_config)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip_adress = socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                            0x8915,
                                            struct.pack('256s', b'wlan0'[:15])
                                            )[20:24])
        print("IP Address: ", self.ip_adress)
        self.comm_handler = comm_handler
        self.sender = "measurement_value/get_Measurement_Value_Video_Values"
        self.getMessages()

        
        self.output = FfmpegOutput(f"-f flv {rtmp_url}")  
        self.output2 = FfmpegOutput(f"-f mpegts udp://138.250.145.156:5000")
        
        self.encoder = H264Encoder()
        self.start_streaming()

    def start_streaming(self):
        self.camera.start_recording(self.encoder, self.output) 
        self.camera.start_recording(self.encoder, self.output2)

    def stop_streaming(self):
        self.camera.stop_recording()

    def on_message(self, client, userdata, message):
        pass

    def getMessages(self):
        def message_loop():  # This function will run in its own thread
            while True:
                self.comm_handler.publish(self.sender, {
                    "Video_HLS_Url": hls_url,
                    "Car_IP_Address": self.ip_adress
                })
                time.sleep(1)  # Sleep within this thread only
        thread = threading.Thread(target=message_loop)
        thread.start()  # Start the thread
    
    def destroy(self):
        self.camera.stop_recording()