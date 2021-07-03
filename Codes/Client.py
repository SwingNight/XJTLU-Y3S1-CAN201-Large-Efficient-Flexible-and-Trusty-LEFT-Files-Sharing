import json
import socket
from socket import *
import time
import threading
from Server import get_file

server_port = 20000


def request(client, ip):
    print('Client: check files list with ', ip)
    client.send('request'.encode())


def receive_file_list(client):
    file_list = client.recv(1024).decode()  # Server.py: client.send(files.encode())
    remote_file = json.loads(file_list)  # Converts a string to a data type
    return remote_file


def stop_request(client, ip):
    client.send('no'.encode())
    client.close()
    print('Client: Stop: do not need to synchronize from', ip)
    time.sleep(1)


def get_file_size(client):
    receive_size = client.recv(1024).decode()  # Server: client.send(str(size).encode())
    file_size = int(receive_size)
    time.sleep(1)
    return file_size


def download(file, size, client, ip):
    receive = 0
    file_temp = open(file, 'wb')
    # To deal with the problem of sticky packet
    while receive < size:
        if size - receive > 1024:
            size_temp = 1024
        else:
            size_temp = size - receive
        data = client.recv(size_temp)
        receive = receive + len(data)
        file_temp.write(data)
    # Finish downloading
    else:
        print('Client: %s is download from %s' % (file, ip))
        file_temp.close()
        time.sleep(1)


def finish(client, ip):
    client.send('finish'.encode())
    print('Client: finish downloading from ', ip)
    client.close()
    time.sleep(1)


def offline(ip):
    print('Offline client: ', ip)
    time.sleep(1)


def connect(ip):
    path = '/home/tc/workplace/cw1/share'
    while True:
        try:
            client = socket(AF_INET, SOCK_STREAM)
            client.connect((ip, server_port))
            time.sleep(0.1)
            # I am A, A want to check files with B
            request(client, ip)
            # B send A its file_list
            remote_file = receive_file_list(client)
            # This is A's file_list
            local_file = get_file(path)
            # I compare A's file_list with B's:
            local_file_size = len(local_file) / 2
            remote_file_size = len(remote_file) / 2  # half is file path, half is mtime
            # if the two file_list have same number of files, A do not need to ask for files
            if local_file_size == remote_file_size:
                stop_request(client, ip)
                break
            # else A will ask for files from B
            for sub_file in remote_file:
                client.send(sub_file.encode())
                # B tell A the size of the file
                file_size = get_file_size(client)
                print('Client: request %s from %s' % (sub_file, ip))
                # download file
                download(sub_file, file_size, client, ip)
            # A finish receiving the files
            finish(client, ip)
            break
        except:
            offline(ip)
            break


def run_client(ip_b, ip_c):
    while True:
        thread_b = threading.Thread(target=connect(ip_b))
        thread_c = threading.Thread(target=connect(ip_c))
        if not thread_b.is_alive():
            thread_c.start()
        if not thread_c.is_alive():
            thread_b.start()
