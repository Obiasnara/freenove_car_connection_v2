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
from libcamera import controls

rtmp_url = "rtmp://157.245.38.231/live/stream1"
hls_url = "https://157.245.38.231/hls/stream1.m3u8"
class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler): 
        self.camera = Picamera2()
        # Set the video configuration
        self.video_config = self.camera.create_video_configuration()
        self.camera.configure(self.video_config)
        self.camera.resolution = (640, 480)
        self.camera.framerate = 60
        self.camera.set_controls({"AfMode":controls.AfModeEnum.Continuous})
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
        self.imageSender = None
        self.encoder = H264Encoder()
        self.encoder.output = self.output
        

    def start_streaming(self):
        self.camera.start_encoder(self.encoder)
        self.camera.start()
        def stream_loop():
            while self.stream:
                if self.imageSender is not None:
                    image = self.camera.capture_array()
                    self.imageSender.send_image(self.hostName, image)
                else:
                    print("ImageSender is None")
        thread = threading.Thread(target=stream_loop)
        thread.start()
    
    def stop_streaming(self):
        self.camera.stop_recording()

    def setUp(self, ip, port):
        self.ip_adress = ip
        self.port = port
        print("IP: ", self.ip_adress)
        print("Port: ", self.port)
        # Connect to the new IP adress and port
        if self.ip_adress != "0.0.0.0" and self.port != -1:
            self.imageSender = imagezmq.ImageSender(connect_to='tcp://'+str(self.ip_adress)+':'+str(self.port))
            self.stream = True
            self.start_streaming()
        else:
            self.stream = False
            self.imageSender.close()
            self.imageSender = None

            

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