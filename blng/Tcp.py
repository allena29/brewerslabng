import socket
import threading
import time
import blng.LogHandler as LogHandler


class Tcp:

    TCP_PORT = 4998
    TCP_ADDRESS = "0.0.0.0"

    def __init__(self, http_port=0, log_component=''):
        self.log = LogHandler.LogHandler(log_component + 'Tcp')
        if http_port:
            self.TCP_PORT = http_port

    def tcp_callback(self, data):
        print('callback_tcp not redefined')

    def serve(self):
        self.log.info('Attempting to bind %s:%s' % (self.TCP_ADDRESS, self.TCP_PORT))
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_server.bind((self.TCP_ADDRESS, self.TCP_PORT))
        self.tcp_server.listen(1)
        self.tcp_server_thread = threading.Thread(target=self.process_client_requests)
        self.tcp_server_thread.daemon = True
        self.tcp_server_thread.start()

    def process_client_requests(self):
        while 1:
            (clientsock, addr) = self.tcp_server.accept()
            self.read_data_and_process_callback(clientsock, addr)
            time.sleep(1)

    def read_data_and_process_callback(self, clientsock, addr):
        data = ""
        while 1:
            d = clientsock.recv(1024)
            if not d:
                break
            data = data + str(d)
            time.sleep(0.1)
        self.tcp_callback(data)

    def end_serve(self):
        self.tcp_server.shutdown()
