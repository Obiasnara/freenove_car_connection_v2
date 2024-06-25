from Handlers.Handler_Interface import Handler_Interface

class HTTP_Handler(Handler_Interface):
    def __init__(self):
        pass

    def on_connect(self, client, userdata, flags, reason_code, properties):
        pass

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        pass

    def on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        pass

    def on_publish(self, client, userdata, mid, reason_code, properties):
        pass

    def publish(self, topic, data):
        pass

    def subscribe(self, topic, on_message=None):
        pass

    def unsubscribe(self, topic):
        pass