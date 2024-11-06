

import numpy as np
import requests
from google.cloud import storage
from concurrent.futures import ProcessPoolExecutor, as_completed
import io 

import sys
sys.path.append("..")

from creds import MAPPER_URL, REDUCER_URL


class Orchestrator():
    def __init__(self, matrix_A, matrix_B, dim_A, dim_B, block_size, mapper_url, reducer_url, bucket_name):
        self.matrix_A = matrix_A
        self.matrix_B = matrix_B
        self.dim_A = dim_A
        self.dim_B = dim_B
        self.block_size = block_size
        self.bucket_name = bucket_name
        self.MAPPER_URL = mapper_url
        self.REDUCER_URL = reducer_url

    @staticmethod
    def retrieve_row_chunks(matrix_dim, block_size):
        rows, cols = matrix_dim
        blocks = [
            (i, j)
            for i in range(rows)
            for j in range(0, cols, block_size)
        ]
        return blocks

    def trigger_map_function(self, a_position, b_position, id):
        i, j = a_position
        start_col, end_col = b_position
        payload = {
            "bucket_name": self.bucket_name,
            "matrix_a": self.matrix_A,
            "matrix_b": self.matrix_B,
            "a_position": (i, j),
            "b_position": (start_col, end_col),
            "id": id
        }

        response = requests.post(self.MAPPER_URL, json=payload)
        return response.status_code, response.text

        # return payload  


    def trigger_reduce_function(self, i, col_start, col_end, files):
        payload = {
            "bucket_name": self.bucket_name,
            "files": files,
            "i": i,
            "j": col_start,
            "j_end": col_end

        }
        # Send a request to the reducer
        response = requests.post(self.REDUCER_URL, json=payload)
        return response.status_code, response.text
    
        # return payload  

    def group_files(self, results):
        grouped = {}
        for file in results:
            i, j, j_end, id = file.replace('.npy', '').replace('Map/', '').split('_')
            
            if (i,j, j_end) in grouped:
                grouped[(i,j, j_end)].append(file)
            else:
                grouped[(i,j, j_end)] = [file]

        return grouped
    
    def reconstruct_matrix(self, reduce_results):

        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        reconstructed_matrix = np.zeros((self.dim_A[0], self.dim_B[1])) 

        for file_path in reduce_results:
            file_name = file_path.split('/')[-1]  
    
            i, j, j_end = map(int, file_name.replace('.npy', '').split('_'))
            
            # Load the partial matrix chunk from storage
            blob = bucket.blob(file_path)
            matrix_bytes = blob.download_as_bytes()
            partial_chunk = np.load(io.BytesIO(matrix_bytes))
            # Place the partial result in the reconstructed matrix
            reconstructed_matrix[i, j:j_end] = partial_chunk

        return reconstructed_matrix

    # def orchestrate_matrix_multiplication(self):
    #     results = []
    #     counter = 0

    #     for a_row, a_col in self.retrieve_row_chunks(self.dim_A, 1):
    #         for col_block_start, col_block_end in [(j, min(j + self.block_size, self.dim_B[1])) for j in range(0, self.dim_B[1], self.block_size)]:

    #             a_block, b_block = (a_row, a_col), (col_block_start, col_block_end)
    #             payload = self.trigger_map_function(a_block, b_block, counter)
    #             results.append(f"Map/{a_row}_{col_block_start}_{col_block_end}_{counter}.npy") 
    #             counter += 1

    #     reduce_results = []
   
    #     for (i, j, j_end), files in self.group_files(results).items():
    #         payload = self.trigger_reduce_function(i, j, j_end, files)
    #         # self.reduce_function(payload)
    #         reduce_results.append(f"Reduce/{i}_{j}_{j_end}.npy")


    #     return self.reconstruct_matrix(reduce_results)
  
    def orchestrate_matrix_multiplication(self):
        results = []
        counter = 0

        # Create a ThreadPoolExecutor for parallel execution of map tasks
        with ProcessPoolExecutor(max_workers=50) as executor:
            map_futures = []
            for a_row, a_col in self.retrieve_row_chunks(self.dim_A, 1):
                for col_block_start, col_block_end in [(j, min(j + self.block_size, self.dim_B[1])) for j in range(0, self.dim_B[1], self.block_size)]:
                    a_block, b_block = (a_row, a_col), (col_block_start, col_block_end)

                    # Submit the trigger_map_function call
                    map_futures.append(executor.submit(self.trigger_map_function, a_block, b_block, counter))
                    results.append(f"Map/{a_row}_{col_block_start}_{col_block_end}_{counter}.npy")
                    counter += 1

            # Wait for all map tasks to complete
            for future in as_completed(map_futures):
                try:
                    result = future.result()  # This will raise any exceptions that occurred
                except Exception as e:
                    print(f"Map task failed: {e}")

        reduce_results = []

        # Create a ThreadPoolExecutor for parallel execution of reduce tasks
        with ProcessPoolExecutor(max_workers=50) as executor:
            reduce_futures = []
            for (i, j, j_end), files in self.group_files(results).items():
                # Submit the cloud function call for reduce tasks
                reduce_futures.append(executor.submit(self.trigger_reduce_function, i, j, j_end, files))
                reduce_results.append(f"Reduce/{i}_{j}_{j_end}.npy")

            # Wait for all reduce tasks to complete
            for future in as_completed(reduce_futures):
                try:
                    result = future.result()  # This will raise any exceptions that occurred
                except Exception as e:
                    print(f"Reduce task failed: {e}")

        return self.reconstruct_matrix(reduce_results)