from abc import ABC, abstractmethod

class MQTTModuleInterface(ABC):
    @abstractmethod
    def on_message(self, client, userdata, message):
        pass

    @abstractmethod
    def getMessages(self):
        pass