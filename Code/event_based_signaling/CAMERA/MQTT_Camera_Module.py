from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import threading
import time
import fcntl
import struct
import socket
from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface
import imagezmq


rtmp_url = "rtmp://157.245.38.231/live/stream1"
hls_url = "https://157.245.38.231/hls/stream1.m3u8"
class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler): 
        self.camera = Picamera2()
        self.video_config = self.camera.create_video_configuration()
        self.camera.configure(self.video_config)
        
        self.hostName = socket.gethostname()
        print("IP Address: ", self.hostName)

        self.comm_handler = comm_handler
        self.sender = "measurement_value/get_Measurement_Value_Video_Values"
        self.receiver = "measurement_value/Video_Values_StartVideoStream"
        self.comm_handler.subscribe(self.receiver, self.on_message)
        self.stream = False
        self.getMessages()

        
        self.output = FfmpegOutput(f"-f flv {rtmp_url}")  
        #self.output2 = FfmpegOutput(f"-f mpegts udp://138.250.145.156:5000 -preset ultrafast -tune zerolatency -x264-params keyint=15:scenecut=0 -fflags nobuffer -probesize 32 -payload_type 96")

        self.imageSender = imagezmq.ImageSender(connect_to='tcp://138.250.145.156:5000')
        self.encoder = H264Encoder()
        self.encoder.output = self.output
        self.start_streaming()

    def start_streaming(self):
        self.camera.start_encoder(self.encoder)
        self.camera.start()
        def stream_loop():
            time.sleep(2)
            while self.stream:
                image = self.camera.capture_array()
                self.imageSender.send_image(self.hostName, image)
        thread = threading.Thread(target=stream_loop)
        thread.start()
    
    def stop_streaming(self):
        self.camera.stop_recording()

    def setUp(self, ip, port):
        self.ip_adress = ip
        self.port = port
        # Connect to the new IP adress and port
        if self.ip_adress != "0.0.0.0" and self.port != -1:
            self.imageSender = imagezmq.ImageSender(connect_to='tcp://'+self.ip_adress+':'+self.port)
            self.stream = True
        else:
            self.stream = False
            

    def getMessages(self):
        def message_loop():  # This function will run in its own thread
            while True:
                self.comm_handler.publish(self.sender, {
                    "Video_HLS_Url": hls_url,
                    "Car_IP_Address": self.hostName
                })
                time.sleep(1)  # Sleep within this thread only
        thread = threading.Thread(target=message_loop)
        thread.start()  # Start the thread
    
    def destroy(self):
        self.camera.stop_recording()