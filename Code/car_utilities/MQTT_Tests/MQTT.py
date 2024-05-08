unacked_publish = set()
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_publish = on_publish

mqttc.user_data_set(unacked_publish)
mqttc.connect("157.245.38.231")
mqttc.loop_start()

i=0;
while True:
    # Our application produce some messages
    # Create the json object
    ultrasonic_data = {
        "distance": i, #ultrasonic.get_distance(),
        "time": time.time()
    }
    msg_info = mqttc.publish("UltraSonicSensor", json.dumps(ultrasonic_data), qos=1)
    unacked_publish.add(msg_info.mid)

    # Wait for all message to be published
    while len(unacked_publish):
        time.sleep(0.1)

    # Due to race-condition described above, the following way to wait for all publish is safer
    msg_info.wait_for_publish()
    i+=1
    time.sleep(1)
    print(f"Published message {i}")

mqttc.disconnect()
mqttc.loop_stop()
print("End of script")