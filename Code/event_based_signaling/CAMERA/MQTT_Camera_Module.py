from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import threading
import time
from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

rtmp_url = "rtmp://157.245.38.231/live/stream1"
class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler): 
        self.comm_handler = comm_handler
        self.sender = "measurement_value/get_Measurement_Value_Video_Values"
        self.getMessages()

        self.camera = Picamera2()
        self.video_config = self.camera.create_video_configuration()
        self.camera.configure(self.video_config)
        
        self.output = FfmpegOutput(f"-f flv {rtmp_url}")  
        self.encoder = H264Encoder()
        self.start_streaming()

    def start_streaming(self):
        self.camera.start_recording(self.encoder, self.output) 

    def stop_streaming(self):
        self.camera.stop_recording()

    def on_message(self, client, userdata, message):
        pass

    def getMessages(self):
        def message_loop():  # This function will run in its own thread
            while True:
                self.comm_handler.publish(self.sender, {"Video_Rtmp_Url": rtmp_url})
                time.sleep(30)  # Sleep within this thread only
        thread = threading.Thread(target=message_loop)
        thread.start()  # Start the thread
    
    def destroy(self):
        self.camera.stop_recording()