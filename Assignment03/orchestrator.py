from google.cloud import storage
from time import perf_counter
import numpy as np
import asyncio
import aiohttp
import tempfile

class Orchestrator():
    def __init__(self, matrix_A, matrix_B, block_size, mapper_url, reducer_url, bucket_name):
        self.matrix_A = matrix_A
        self.matrix_B = matrix_B
        self.dim_A = self.matrix_A.shape
        self.dim_B = self.matrix_B.shape
        self.block_size = block_size
        self.MAPPER_URL = mapper_url
        self.REDUCER_URL = reducer_url
        self.bucket_name = bucket_name


    @staticmethod
    def retrieve_elems(matrix):
        blocks = [
            (i, j)
            for i in range(len(matrix))
            for j in range(len(matrix[i]))
        ]
        return blocks

    async def trigger_map_function(self, session, a_chunk, b_chunk, i, j, start_chunk, end_chunk):
        payload = {
            "matrix_a_chunk": a_chunk.tolist(),
            "matrix_b_chunk": b_chunk.tolist(),
        }
        async with session.post(self.MAPPER_URL, json=payload) as response:
            if response.status == 200:
                return ((i, start_chunk, end_chunk), np.array(await response.json()))
            else:
                raise Exception(f"Map function failed: {response.status}, {await response.text()}")

    async def trigger_reduce_function(self, session, partial_results, i, start_chunk, end_chunk):
        payload = {
            "partial_results": [result.tolist() for result in partial_results]
        }
        async with session.post(self.REDUCER_URL, json=payload) as response:
            if response.status == 200:
                return ((i, start_chunk, end_chunk), np.array(await response.json()))
            else:
                raise Exception(f"Reduce function failed: {response.status}, {await response.text()}")

    async def mapper(self):
        partial_results = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for a_row, a_col in self.retrieve_elems(self.matrix_A):
                for col_block_start, col_block_end in [(j, min(j + self.block_size, self.dim_B[0])) for j in range(0, self.dim_B[0], self.block_size)]:
                    a_chunk = self.matrix_A[a_row, a_col]
                    b_chunk = self.matrix_B[a_col, col_block_start:col_block_end]
                    tasks.append(self.trigger_map_function(session, a_chunk, b_chunk, a_row, a_col, col_block_start, col_block_end))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    print(f"Map task failed: {result}")
                else:
                    partial_results.append(result)

        return partial_results

    async def reducer(self, grouped_results):
        final_results = {}
        async with aiohttp.ClientSession() as session:
            tasks = []
            for (i, col_block_start, col_block_end), group in grouped_results.items():
                tasks.append(self.trigger_reduce_function(session, group, i, col_block_start, col_block_end))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    print(f"Reduce task failed: {result}")
                else:
                    (i, col_block_start, col_block_end), chunk = result
                    final_results[(i, col_block_start, col_block_end)] = chunk

        return final_results

    def grouper(self, partial_results):
        grouped_results = {}
        for (i, col_block_start, col_block_end), result in partial_results:
            if (i, col_block_start, col_block_end) not in grouped_results:
                grouped_results[(i, col_block_start, col_block_end)] = []
            grouped_results[(i, col_block_start, col_block_end)].append(result)

        return grouped_results

    def reconstruct(self, final_results):
        reconstructed_matrix = np.zeros((self.dim_A[0], self.dim_B[1]))
        for (i, j_start, j_end), chunk in final_results.items():
            reconstructed_matrix[i, j_start:j_end] = chunk

        return reconstructed_matrix

    async def orchestrate_matrix_multiplication(self):

        time = perf_counter()
        partial_results = await self.mapper()
        map = perf_counter() - time

        grouped = self.grouper(partial_results)

        time = perf_counter()
        final_results = await self.reducer(grouped)
        reduce = perf_counter() - time

        reconstructed = self.reconstruct(final_results)
        return reconstructed, map, reduce
    
    def save_to_bucket(self, matrix, destination_blob_name):
        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)

        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            np.save(tmpfile.name, matrix)
            blob.upload_from_filename(tmpfile.name)