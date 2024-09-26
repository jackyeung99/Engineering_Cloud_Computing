from socket import *



def send_get_command(server_port, key):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(('', server_port))
    command = f"get {key}\r\n"
    clientSocket.sendall(command.encode('utf-8'))
    response = clientSocket.recv(1024).decode('utf-8')
    clientSocket.close()

    return response

def send_set_command(server_port, key, value):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(('', server_port))
    command = f"set {key} {len(value)}\r\n{value}\r\n"
    clientSocket.sendall(command.encode('utf-8'))
    response = clientSocket.recv(1024).decode('utf-8')
    clientSocket.close()

    return response



if __name__ == '__main__':

    send_set_command(9889, 'test_key', 'test_val')
    send_get_command(9889, 'test_key')