import socket
import pytest
import threading
import time
import os
import sys

repo_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(repo_root)

from server import TCPServer
from client import TCPClient

@pytest.fixture(scope="session", autouse=True)
def start_server():
    server_thread = threading.Thread(target=lambda: TCPServer(9889).start_server())
    server_thread.daemon = True  
    server_thread.start()
    time.sleep(1)  
    yield


def test_set_command(start_server):
    with TCPClient(9889) as client:
        response = client.send_set_command('testkey', 'testvalue')
    
    assert response == 'STORED\r\n'

def test_get_command(start_server):
    # Test setting and getting a value
    with TCPClient(9889) as client:
        client.send_set_command('testkey', 'testval')
        response = client.send_get_command('testkey')
        expected_size = len('testval'.encode('utf-8'))

    expected_response = f'VALUE testkey 0 {expected_size}\r\ntestval\r\nEND\r\n'

    assert response == expected_response

def test_get_nonexistent_key(start_server):
    client = TCPClient(9889)
    response = client.send_get_command('nonexistent')
    client.close()
    assert response == 'END\r\n'  

def client_one():
    client = TCPClient(9889)
    client.send_set_command('client1_key', 'client1_value')
    response = client.send_get_command('client1_key')
    expected_size = len('client1_value')
    expected_response = f'VALUE client1_key 0 {expected_size}\r\nclient1_value\r\nEND\r\n'
    client.close()
    assert response == expected_response

def client_two():
    client = TCPClient(9889)
    client.send_set_command('client2_key', 'client2_value')
    response = client.send_get_command('client2_key')
    expected_size = len('client2_value'.encode('utf-8'))
    expected_response = f'VALUE client2_key 0 {expected_size}\r\nclient2_value\r\nEND\r\n'
    client.close()
    assert response == expected_response

# Test to run two clients concurrently
def test_two_clients_concurrently(start_server):
    client1_thread = threading.Thread(target=client_one)
    client2_thread = threading.Thread(target=client_two)
    
    client1_thread.start()
    client2_thread.start()
    
    client1_thread.join()
    client2_thread.join()