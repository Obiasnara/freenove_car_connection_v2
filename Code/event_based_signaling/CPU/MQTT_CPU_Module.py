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
        self.sender = "measurement_value/get_Measurement_Value_CPU_Values"
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
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        if proc.info['cpu_percent'] > 0:
                            most_cpu_intensive_processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                most_cpu_intensive_processes = sorted(most_cpu_intensive_processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]

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
                time.sleep(1)  # Sleep within this thread only

        thread = threading.Thread(target=message_loop)
        thread.start()  # Start the thread

    def on_message(self, client, userdata, message):
        pass

    def destroy(self):
        self.mqtt_handler.stop()