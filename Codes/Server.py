import json
import time
import threading
from socket import *
from os import listdir
from os.path import isfile, join, getmtime, getsize

client_socket = []

server_port = 20000
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)  # Reuse
server_socket.bind(("", server_port))
server_socket.listen(10)  # Connection queue


def get_file(the_path):
    files = []
    file_list = listdir(the_path)
    for file in file_list:  # Traverse the file list
        file_path = join(the_path, file)
        if isfile(file_path):
            files.append(file_path)  # append() can only add element
            file_time = getmtime(file_path)
            files.append(file_time)
        else:
            files.extend(get_file(file_path))  # extend() can add a list
    return files


def response_request(path, client, ip):
    print("Server: receive the request for file list %s from %s" % (path, ip))
    file_list = get_file(path)
    files = json.dumps(file_list)  # Converts a data type to a string
    client.send(files.encode())
    print("Server: file list %s send successfully to %s" % (file_list, ip))
    time.sleep(1)


def response_no(ip):
    print('Server: no need to send file list to ', ip)
    time.sleep(1)


def response_size(file, client, ip):
    # Tell B the size of the file
    print('Server: send %s the size of %s' % (ip, file))
    size = getsize(file)  # The size of a file in bytes
    client.send(str(size).encode())  # Converts the size to string and then converts it to bytes


def upload(file_path, client, ip):
    print('Server: send %s the file %s' % (ip, file_path))
    file = open(file_path, 'rb')
    for line in file:
        client.send(line)
    print('Server: %s is upload to %s' % (file_path, ip))
    file.close()
    time.sleep(1)


def response_file(file, client, ip):
    response_size(file, client, ip)
    upload(file, client, ip)


def response_finish(ip):
    print("Server: all files have sent to", ip)
    time.sleep(1)


def listen(client):
    socket_temp = client[0]
    ip_temp = client[1]
    path = '/home/tc/workplace/cw1/share'
    while True:
        try:
            receive = socket_temp.recv(1024).decode()
            # I am A, if B tell A it need to check file_list, A will send it to B
            if receive == 'request':
                response_request(path, socket_temp, ip_temp)
                continue

            # B tell A it do not need to synchronized files
            elif receive == "no":
                response_no(ip_temp)
                break

            # B send A the file_name it ask for
            elif isfile(receive):  # client_socket.send(sub_file.encode())
                response_file(receive, socket_temp, ip_temp)
                continue

            # B tell A it finish downloading files
            elif receive == "finish":
                response_finish(ip_temp)
                break
        except:
            break


def run_server():
    while True:
        socket_a, ip = server_socket.accept()  # Waiting to receive connection
        print("* Online client: ", ip)
        socket_b = [socket_a, ip]
        client_socket.append(socket_b)
        for i in client_socket:  # Global variable
            thread = threading.Thread(target=listen, args=(i,))  # Pass parameter
            thread.start()
            client_socket.remove(i)  # Prevent duplication with the next user_socket
