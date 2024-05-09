import paho.mqtt.client as mqtt

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    print(f"Subscribe acknowledged: {mid}")
    def on_message(client, userdata, message):
        # userdata is the structure we choose to provide, here it's a list()
        userdata.append(message.payload)
        print(f"Received message: {message.payload}")
    
    mqttc.on_message = on_message
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    # Be careful, the reason_code_list is only present in MQTTv5.
    # In MQTTv3 it will always be empty
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")
    client.disconnect()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        # we should always subscribe from on_connect callback to be sure
        # our subscribed is persisted across reconnections.
        client.subscribe("MotorC")
        client.subscribe("MotorP")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.enable_logger()
mqttc.on_connect = on_connect

mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

mqttc.user_data_set([])
mqttc.connect("157.245.38.231")

mqttc.loop_forever()
print(f"Received the following message: {mqttc.user_data_get()}")