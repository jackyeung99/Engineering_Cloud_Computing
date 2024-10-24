import time
import random 
import pandas as pd


# from creds import SERVER_IP, BUCKET_NAME
from client import TCPClient
from google_kv import GCPBlobKVStore




def speed_test(client):
    start_time = time.time()
    for i in range(1000):
        client.set(f'key{i}', f'value{i}')
        client.get(f'key{i}')
    end_time = time.time()

    return end_time - start_time

def arrival_rate_test(client):

    num_requests = 1000
    arrival_rates = [10, 20, 30, 50, 70, 90] 

    results = []
    for arrival_rate in arrival_rates:
        total_response_time = 0
        
        for i in range(num_requests):
            start_time = time.time()
            
            client.set(f'key{i}', f'value{i}')
            
            end_time = time.time()
            response_time = end_time - start_time
            total_response_time += response_time
            
            time.sleep(1/arrival_rate)
        
        avg_response_time = total_response_time / num_requests
        results.append((arrival_rate, avg_response_time))

    return pd.DataFrame(results)



if __name__ == '__main__':
        
    SERVER_IP = input('IP Address: ')
    client = TCPClient(SERVER_IP, 9889).__enter__()

    # Run arrival rate test
    df = arrival_rate_test(client)
    df.to_csv('arrival_rate.csv', index=False)  # Save results to CSV
    print(f"Arrival rate test results saved to 'arrival_rate.csv'.")

    # Run speed test for TCP
    tcp_speed = speed_test(client)
    print(f"TCP speed test duration: {tcp_speed} seconds")
    client.__exit__()

    # Initialize the Google KV store and run speed test
    BUCKET_NAME = input('BUCKET: ')
    kv_store = GCPBlobKVStore(BUCKET_NAME)
    kv_speed = speed_test(kv_store)
    print(f"Google KV store speed test duration: {kv_speed} seconds")
