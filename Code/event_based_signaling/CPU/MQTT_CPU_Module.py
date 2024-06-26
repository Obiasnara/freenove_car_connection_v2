import time
import threading
import psutil
from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

class CPU(MQTT_Module_Interface):
    def __init__(self, comm_handler):
        self.comm_handler = comm_handler
        self.sender = "Submodel1_Operation5"
        self.CPU_temp = 0
        self.CPU_usage = 0
        self.getMessage()

    def getMessage(self):
        def message_loop():  # This function will run in its own thread
            while True:
                CPU_pids = psutil.pids()
                CPU_usage = psutil.cpu_percent()
                if CPU_pids != self.CPU_temp or CPU_usage != self.CPU_usage:
                    self.CPU_temp = CPU_pids
                    self.CPU_usage = CPU_usage
                    self.comm_handler.publish(self.sender, str(CPU_pids) + "_" + str(CPU_usage))
                time.sleep(1)  # Sleep within this thread only

        thread = threading.Thread(target=message_loop)
        thread.start()  # Start the thread

    def on_message(self, client, userdata, message):
        pass

    def destroy(self):
        self.mqtt_handler.stop()