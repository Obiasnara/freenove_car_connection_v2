from abc import ABC, abstractmethod

class HandlerInterface(ABC):
    @abstractmethod
    def on_connect(self, client, userdata, flags, reason_code, properties):
        pass  # No implementation here, just a declaration

    @abstractmethod
    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        pass 

    @abstractmethod
    def on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        pass

    @abstractmethod
    def on_publish(self, client, userdata, mid, reason_code, properties):
        pass

    @abstractmethod
    def publish(self, topic, data):
        pass

    @abstractmethod
    def subscribe(self, topic, on_message=None):
        pass

    @abstractmethod
    def unsubscribe(self, topic):
        pass
