import time
import threading
import psutil
from Interfaces.MQTT_Module_Interface import MQTT_Module_Interface

# We want to gather informations about the CPU usage and the PIDs of the processes
# pids()
# cpu_percent()
# cpu_stats()
# cpu_freq()
# getloadavg()
# virtual_memory()
# swap_memory()
# disk_usage()
# disk_partitions()
# disk_io_counters()
# net_io_counters()
# boot_time()
# users()
# sensors_temperatures()
# sensors_fans()

class CPU(MQTT_Module_Interface):
    def __init__(self, comm_handler):
        self.comm_handler = comm_handler
        self.sender = "Submodel1_Operation5"
        self.getMessage()

    def getMessage(self):
        def message_loop():  # This function will run in its own thread
            while True:
                pids = psutil.pids()
                cpu_percent = psutil.cpu_percent()  # This is the function that will be called every second
                cpu_stats = psutil.cpu_stats()
                cpu_freq = psutil.cpu_freq()
                getloadavg = psutil.getloadavg()
                virtual_memory = psutil.virtual_memory()
                swap_memory = psutil.swap_memory()
                disk_usage = psutil.disk_usage('/')
                disk_partitions = psutil.disk_partitions()
                disk_io_counters = psutil.disk_io_counters()
                net_io_counters = psutil.net_io_counters()
                boot_time = psutil.boot_time()
                users = psutil.users()
                sensors_temperatures = psutil.sensors_temperatures()
                sensors_fans = psutil.sensors_fans()
                # 10 most CPU-intensive processes
                most_cpu_intensive_processes = []
                i=0
                # Sort the processes by CPU usage
                for proc in sorted([psutil.Process(pid) for pid in pids], key=lambda proc: proc.info['cpu_percent'], reverse=True):
                    if i == 10:
                        break
                    most_cpu_intensive_processes.append({
                        "pid": proc.pid,
                        "name": proc.name(),
                        "cpu_percent": proc.info['cpu_percent']
                    })
                    i += 1
                    

                # Agregate the data in a JSON format
                data = {
                    "pids": pids,
                    "most_cpu_intensive_processes": most_cpu_intensive_processes, # "most_cpu_intensive_processes": "pid", "name", "cpu_percent
                    "cpu_percent": cpu_percent,
                    "cpu_stats": cpu_stats,
                    "cpu_freq": cpu_freq,
                    "getloadavg": getloadavg,
                    "virtual_memory": virtual_memory,
                    "swap_memory": swap_memory,
                    "disk_usage": disk_usage,
                    "disk_partitions": disk_partitions,
                    "disk_io_counters": disk_io_counters,
                    "net_io_counters": net_io_counters,
                    "boot_time": boot_time,
                    "users": users,
                    "sensors_temperatures": sensors_temperatures,
                    "sensors_fans": sensors_fans
                }
                self.comm_handler.publish(self.sender, data)
                time.sleep(5)  # Sleep within this thread only

        thread = threading.Thread(target=message_loop)
        thread.start()  # Start the thread

    def on_message(self, client, userdata, message):
        pass

    def destroy(self):
        self.mqtt_handler.stop()