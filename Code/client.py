import atexit
import pickle
import socket
import struct
import cv2
import numpy as np
from threading import *
from .enumerate import *
from .data.packet import *
from .data.database import *


def class_threading(func):
    def wrapper(self, *args, **kwargs):
        thread = Thread(target=func, args=(self, *args,), kwargs=kwargs)
        thread.start()

    return wrapper


def start_tcp_client(ip, port):
    """
    Open a new client socket and try to connect to the given ip and port
    Return the connection
    """
    print(f'Connecting to {ip}:{port}...')
    client = socket.socket()
    try :
        client.connect((ip, port))
        print(f'Connected to {ip}:{port}')
        return client
    except Exception as e:
        print(f'Connection to {ip}:{port} failed')
        print(e)
        return None
    


class Client:

    def __init__(self, ip, port=Port.PORT_COMMAND.value, video_port=Port.PORT_VIDEO.value,
                 data_port=Port.PORT_DATA.value):
        # init_db()
        self.server_ip = ip
        self.video_port = video_port
        self.client = start_tcp_client(ip, port)
        self.video_client = None
        self.client_data_socket = None
        self.last_state = None
        self.data_collection_bool = False
        self.timer = 1
        self.imgbytes = None
        self.data_collection(ip, data_port)
        self.initialised = True

    def connect_to_video_server(self, framerate, width, height):
        self.video_client = start_tcp_client(self.server_ip, self.video_port)
        camera_data = d.Data.CameraData()
        d.Data.set_camera_data(camera_data, framerate=framerate, width=width, height=height)
        self.video_client.send(pickle.dumps(camera_data))
        self.start_recording()

    @class_threading
    def start_recording(self):
        n_img = 0
        directory = str(d.datetime.now())
        os.mkdir(f'./{directory}')
        with self.video_client.makefile('rb') as connection:
            while True:
                try:
                    stream_bytes = connection.read(4)
                    frame_length = struct.unpack('<L', stream_bytes[:4])
                    self.imgbytes = connection.read(frame_length[0])
                    image = cv2.imdecode(np.frombuffer(self.imgbytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                    cv2.imwrite(f'{directory}/{n_img}.jpg', image)
                    n_img += 1
                    # showing camera live
                    # cv2.imshow('image', image)
                    # if cv2.waitKey(10) == 13:
                    #     break
                except Exception as e:
                    print(e)
                    cv2.destroyAllWindows()
                    break

    @class_threading
    def data_collection(self, ip, port):
        """
        Open a socket and try to connect to the given IP at the port 5005
        When connected, request for the current state of the car every "timer" value in seconds
        Add an atexit function to call to close the data
        """

        onto = start_database()
        atexit.register(stop_database)
        while True:
            self.client_data_socket = start_tcp_client(ip, port)
            try:
                while True:
                    self.client_data_socket.send(Command.CMD_DATA.value.encode("utf-8"))
                    serialized_data = self.client_data_socket.recv(1024)
                    if not serialized_data:
                        print("Connexion with server lost...")
                        break
                    data = pickle.loads(serialized_data)
                    set_data(data, sampl_rate=self.timer)
                    self.last_state = data
                    if self.data_collection_bool:
                        add_car_data_to_db(data=data, onto=onto)
                        default_world.save()
                    # print_data(self.last_state)
                    time.sleep(self.timer)
            except socket.error as e:
                print("Connexion error :", str(e))
                print("Trying to reconnect in 5 seconds...")
                time.sleep(5)
                continue

    def send_msg(self, data):
        """
        data shape : Command.CMD_XXX.value YYY_YYY_YYY_YYY
        """
        n = self.client.send(data.encode('utf-8'))
        if n != len(data):
            print('sending error')

    def close_data_connection(self):
        self.client_data_socket.shutdown(socket.SHUT_RDWR)
        self.client_data_socket.close()

    def close_video_connection(self):
        self.video_client.shutdown(socket.SHUT_RDWR)
        self.video_client.close()

    def close_connection(self):
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()

    async def get_last_state(self):
        while self.last_state is None:
            continue
        return self.last_state


if __name__ == '__main__':
    client_ui = Client()
    client_ui.setup("138.250.151.95")
    # client_ui.setup(sys.argv[1])
