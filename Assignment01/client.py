import socket
import time
import numpy as np 

class TCPClient:

    def __init__(self, host,  serverPort):
        self.serverPort = serverPort
        self.host = host
        self.client_socket = None
        

    # Using with command to deal with opening and closing of connections
    def __enter__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.serverPort))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client_socket.close()

    def get(self, key):
       
        command = f"get {key}\r\n"
        self.client_socket.sendall(command.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
  
        return response

    def set(self, key, value):
    
        flags = 0 
        exptime = 0 
        bytes_len = len(value)
        command = f"set {key} {flags} {exptime} {bytes_len}\r\n{value}\r\n"
        self.client_socket.sendall(command.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
   
        return response


if __name__ == '__main__':\

    times = []
    with TCPClient(9889) as client:
        for n in range(100):
            start_time = time.perf_counter()
            set_response = client.set(f'test_key', 'test_val')
            processing_time = time.perf_counter() - start_time 
            times.append(processing_time)
            # print(f"SET Response: {set_response}")

        # get_response = client.send_get_command('test_key')
        # print(f"GET Response: {get_response}")

    print(np.mean(times) * 1000)
    



  