import os
import socket
import time
import random
import argparse

class TCPServer:

    def __init__(self, port_number):
        self.port_number = port_number
        self.start_server()

    def random_delay(self):
        time.sleep(random.uniform(0, 1))


    def get(self, key, no_reply=False):
        file_path = os.path.join('keys', f"{key}.txt")
        if not os.path.exists(file_path):
            return "END\r\n"
        
        with open(file_path, 'r') as f:
            data = f.read().split(' ', 1)
            flags = data[0]
            value = data[1]
            value_size = len(value)
            response = f"VALUE {key} {flags} {value_size}\r\n{value}\r\nEND\r\n"
   
        if not no_reply:
            return response

    def set(self, key, value, flags='', no_reply=False):
        file_path = os.path.join('keys', f"{key}.txt")
        with open(file_path, 'w') as f:
            f.write(f"{flags} {value}")

        if not no_reply:
            return "STORED\r\n"
        else:
            return True

    def process_command(self, command_str):
        self.random_delay()
        commands = command_str.strip().split()

        if commands[0].lower() == 'set':
            print(commands)
            key = commands[1]
            flags = commands[2]
            exptime = commands[3]
            value_size = int(commands[4])
            value = commands[5]
            return self.set(key, value, flags)
        elif commands[0].lower() == 'get':
            key = commands[1]
            print(key)
            return self.get(key)
        
        return "ERROR\r\n"


    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', self.port_number))
        server_socket.listen(1)

        try:
            while True:
                connection_socket, addr = server_socket.accept()

                #allow multiple commands from same client
                while True:  
                    command = connection_socket.recv(1024).decode('utf-8')
                    if not command:
                        break  

                    response = self.process_command(command)
                    connection_socket.send(response.encode('utf-8'))

                connection_socket.close()
          
                

        except KeyboardInterrupt:
            print("Shutting Down")
        finally:
            server_socket.close()

if __name__ == '__main__':
    if not os.path.exists('keys'):
        os.makedirs('keys') 

    server = TCPServer(9889)
 
