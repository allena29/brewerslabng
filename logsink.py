
import socket
import time

IP = '127.0.0.1'
PORT = 6666
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((IP, PORT))

while True:
    data, addr = sock.recvfrom(1024)
    print(data[:100])
    time.sleep(0.015)
