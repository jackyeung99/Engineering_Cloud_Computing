from socket import *
import os 
import sys
import random
import time

def random_delay():
    time.sleep(random.uniform(0, 1))

def set_key(key, val):
    file_path = os.path.join('keys', f'{key}.txt' )
    with open(file_path, "w") as f:
        f.write(val)

def get_key(key):
    file_path = os.path.join('keys', f'{key}.txt' )
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    else:
        return None

def process_get_command(key):
    try:
        val = get_key(key)
        size = len(val)
        return f'VALUE {key} {size}\r\n{val}\r\nEND\r\n'
    except:
        return 'NONE\r\nEND\r\n'
def process_set_command(key, val):
    try:
        set_key(key, val)
        return 'STORED\r\n'
    except:
        return 'NOT-STORED\r\n'

def process_command(text_str):
    random_delay()
    command_str = text_str.decode('utf-8').strip()
    command_parts = command_str.split()

    if command_parts[0].lower() == 'get' and len(command_parts) == 2:
        return process_get_command(command_parts[1])
    elif command_parts[0].lower() == 'set' and len(command_parts) == 4:
        return process_set_command(command_parts[1], command_parts[3])


def run_server(serverPort):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(1)
    while 1:
        try:
            connectionSocket, addr = serverSocket.accept()
            sentence = connectionSocket.recv(1024)

            output = process_command(sentence)
            connectionSocket.send(output.encode('utf-8'))
        except:
            break
     
    connectionSocket.close()



if __name__ == '__main__':

    run_server(9889)
