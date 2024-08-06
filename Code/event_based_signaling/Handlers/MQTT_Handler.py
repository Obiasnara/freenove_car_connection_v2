import time
import json
import paho.mqtt.client as mqtt
from Interfaces.Handler_Interface import HandlerInterface

class MQTTHandler(HandlerInterface):
    
    def __init__(self, broker_address="localhost", client_id="", qos=1):
        self.broker_address = broker_address
        self.client_id = client_id
        self.qos = qos
        self.unacked_publish = set()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_publish = self.on_publish
        self.client.user_data_set(self.unacked_publish)
        self.client.enable_logger()
        self.client.connect(self.broker_address)
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
        self.client.on_message = self.on_message
        self.client.loop_start()

    def on_publish(self, client, userdata, mid, reason_code, properties):
        try:
            userdata.remove(mid)
        except KeyError:
            print("on_publish() is called with a mid not present in unacked_publish")


    def setElements(self, elements):
        self.elements = elements
        print(f"Elements set: {self.elements}")

    def getElement(self, element_name):
        return self.elements.get(element_name)

    def on_message(self, client, userdata, message):
        print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

        try:
            data = json.loads(message.payload.decode())

            # Action Dictionary (Mapping topics to functions)
            actions = {
                "measurement_value/Engines_Values_ChangeRotationSpeeds": lambda: self.getElement("Motor").setMotorModel(
                    data.get("FrontLeftWheelDuty"),
                    data.get("BackLeftWheelDuty"),
                    data.get("FrontRightWheelDuty"),
                    data.get("BackRightWheelDuty"),
                ),
                # Add more actions for other topics here...
            }

            # Execute Action Based on Topic
            action_function = actions.get(message.topic)
            if action_function:
                action_function()
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON message: {e}")

        except KeyError as e:
            print(f"Missing key in JSON message for topic '{message.topic}': {e}")

  
    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        print(f"Subscribe acknowledged: {mid}")

        if reason_code_list[0].is_failure:
            print(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
            print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
        else:
            print(f"Broker replied with failure: {reason_code_list[0]}")
        client.disconnect()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")

    def publish(self, topic, data):
        try:
            msg_info = self.client.publish(topic, json.dumps(data), qos=self.qos)
            self.unacked_publish.add(msg_info.mid)
            self.wait_for_publish()
        except Exception as e:
            print(f"Error publishing data to topic {topic}: {e}")

    def subscribe(self, topic, on_message=None):
        print(f"Subscribing to topic {topic}")
        self.client.subscribe(topic)

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)

    def wait_for_publish(self):
        while len(self.unacked_publish) > 0:
            time.sleep(0.1)

    def disconnect(self):
        self.client.disconnect()

    def stop(self):
        self.disconnect()
        self.client.loop_stop()
        print("MQTT client stopped")
