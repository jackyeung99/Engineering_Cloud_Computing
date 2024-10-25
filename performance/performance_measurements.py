import time
import random 
import pandas as pd
import os 
import sys
from concurrent.futures import ThreadPoolExecutor

repo_root =os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(repo_root)

# from creds import SERVER_IP, BUCKET_NAME
from client import TCPClient
from google_kv import GCPBlobKVStore



def get_speed(client):
    get_time = 0.0 
    for i in range(100):
        start_time = time.perf_counter()
        client.set(f"key{i}", f"value{i}")
        end_time = time.perf_counter() - start_time

        get_time += end_time

    return get_time/100

def set_speed(client):
    get_time = 0.0 
    for i in range(100):
        start_time = time.perf_counter()
        client.get(f"key{i}")
        end_time = time.perf_counter() - start_time

        get_time += end_time

    return get_time/100


def speed_test(client):
    start_time = time.time()
    for i in range(100):
        client.set(f'key{i}', f'value{i}')
        client.get(f'key{i}')
    end_time = time.time()

    return end_time - start_time

def arrival_rate_test(client):

    num_requests = 100
    arrival_rates = [10, 20, 30, 50, 70, 80, 90, 100, 250, 1000, 10000, 50000]


    results = []
    for arrival_rate in arrival_rates:
        total_response_time = 0
        num_failed_requests = 0
        
        print(f"Testing arrival rate: {arrival_rate} requests/second")
        
        for i in range(num_requests):
            try:
        
                start_time = time.perf_counter()
             
                client.set(f'key{i}', f'value{i}')
                client.get(f'key{i}')

                end_time = time.perf_counter()
                
                response_time = end_time - start_time
                total_response_time += response_time

            except Exception as e:
                print(f"Request {i} failed: {e}")
                num_failed_requests += 1

            # Sleep to simulate arrival rate
            inter_arrival_time = 1 / arrival_rate
            time.sleep(inter_arrival_time)
        

        successful_requests = num_requests - num_failed_requests
        if successful_requests > 0:
            avg_response_time = total_response_time / successful_requests
        else:
            avg_response_time = None 


        results.append((arrival_rate, avg_response_time, num_failed_requests))


    return pd.DataFrame(results, columns=["Arrival Rate", "Avg Response Time (s)", "Failed Requests"])


def send_request(client, server_ip, i):
    try:
        # Create a TCP client and set/get key-value pair
        with client(server_ip, 9889) as client:
            client.set(f'key{i}', f'value{i}')
            client.get(f'key{i}')
        
        return
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to measure the requests per second
def measure_rps(client, server_ip, num_requests, num_threads):
    # Start time
    start_time = time.time()
    
    # Use ThreadPoolExecutor to send requests in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_request, client, server_ip, i) for i in range(num_requests)]
        
        # Wait for all threads to complete
        for future in futures:
            future.result()
    
    # End time
    end_time = time.time()
    
    # Calculate time taken and RPS
    time_taken = end_time - start_time
    rps = num_requests / time_taken if time_taken > 0 else 0
    return rps, time_taken


if __name__ == '__main__':
        
    SERVER_IP = input('IP Address: ') 
    concurrency_levels = [1, 10, 50, 100, 200]  # Change as needed
    NUM_REQUESTS = 100
    for num_threads in concurrency_levels:
        rps, time_taken = measure_rps(TCPClient, SERVER_IP, NUM_REQUESTS, num_threads)
        print(f"Concurrency: {num_threads}, Requests per second: {rps:.2f}, Time taken: {time_taken:.2f} seconds")



        
    # with TCPClient(SERVER_IP, 9889) as client:

        # Run arrival rate test
        # df = arrival_rate_test(SERVER_IP)
        # df.to_csv('arrival_rate.csv', index=False)  # Save results to CSV
        # print(f"Arrival rate test results saved to 'arrival_rate.csv'.")

        # # Run speed test for TCP
        # set = set_speed(client)
        # print(f"TCP set speed {set}")

        # get = get_speed(client)
        # print(f"TCP get speed {get}")

        # tcp_speed = speed_test(client)
        # print(f"TCP speed test duration: {tcp_speed} seconds")
  

    # # Initialize the Google KV store and run speed test
    # BUCKET_NAME = 'jack-fall2024'
    # kv_store = GCPBlobKVStore(BUCKET_NAME)
    
    # set = set_speed(kv_store)
    # print(f"Google KV set speed {set}")

    # get = get_speed(kv_store)
    # print(f"Google KV get speed {get}")

    # kv_speed = speed_test(kv_store)
    # print(f"Google KV store speed test duration: {kv_speed} seconds")
