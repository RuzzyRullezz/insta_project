import socket
from contextlib import closing


def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex((host, port)) == 0


def is_port_open(port):
    return not check_socket('127.0.0.1', port)
