from abc import ABC, abstractmethod

class MQTT_Module_Interface(ABC):
    @abstractmethod
    def on_message(self, client, userdata, message):
        pass

    @abstractmethod
    def getMessages(self):
        pass

    @abstractmethod
    def destroy(self):
        pass