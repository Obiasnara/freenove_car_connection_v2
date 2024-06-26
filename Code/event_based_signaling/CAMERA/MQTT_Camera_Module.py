import cv2
from picamera2 import Picamera2


from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

class Camera(MQTT_Module_Interface):
    def __init__(self, comm_handler):
        self.comm_handler = comm_handler
        self.sender = "Submodel1_Operation6"

        self.camera = Picamera2.cv2
        
        

    def on_message(self, client, userdata, message):
        if message.topic == self.mqtt_topic:
            self.camera.take_picture()
            self.camera.send_picture()
            self.camera.delete_picture()

    def getMessages(self):
        pass
    
    def destroy(self):
        pass