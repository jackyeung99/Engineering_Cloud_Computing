import socket
import pytest
import threading
import time
import os
import sys

repo_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(repo_root)

from server import run_server
from client import send_get_command, send_set_command

@pytest.fixture(scope="session", autouse=True)
def start_server():
    server_thread = threading.Thread(target=run_server, kwargs={'serverPort': 9889})
    server_thread.daemon = True  
    server_thread.start()
    time.sleep(1)  
    yield


def test_set_command(start_server):
    response = send_set_command(9889, 'testkey', 'testvalue')
    assert response == 'STORED\r\n'

def test_get_command(start_server):
    #test get and rewrite
    send_set_command( 9889, 'testkey', 'testval')
    response = send_get_command (9889, 'testkey')
    expected_size = len('testval'.encode('utf-8'))
    expected_response = f'VALUE testkey {expected_size}\r\ntestval\r\nEND\r\n'  
    assert response == expected_response

def test_get_nonexistent_key(start_server):
    response = send_get_command( 9889, 'nonexistent')
    assert response == 'NONE\r\nEND\r\n'