from abc import ABC, abstractmethod

class MQTT_Module_Interface(ABC):
    def on_message(self, client, userdata, message):
        pass

    def getMessages(self):
        pass

    def destroy(self):
        pass