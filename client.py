import socket

class TCPClient:

    def __init__(self, serverPort):
        self.serverPort = serverPort
        self.client_socket = None
 

    # Using with command to deal with opening and closing of connections
    def __enter__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', self.serverPort))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client_socket.close()

    def send_get_command(self, key):
       
        command = f"get {key}\r\n"
        self.client_socket.sendall(command.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
  
        return response

    def send_set_command(self, key, value):
    
        flags = 0 
        exptime = 0 
        bytes_len = len(value)
        command = f"set {key} {flags} {exptime} {bytes_len}\r\n{value}\r\n"
        self.client_socket.sendall(command.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
   
        return response


if __name__ == '__main__':
    client = TCPClient(9889)
    set_response = client.send_set_command('test_key', 'test_val')
    print(f"SET Response: {set_response}")

    client = TCPClient(9889) 
    get_response = client.send_get_command('test_key')
    print(f"GET Response: {get_response}")