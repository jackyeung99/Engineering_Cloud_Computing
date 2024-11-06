import numpy as np
from google.cloud import storage
import io

def map_matrix_multiplication(request):
    """Map function to multiply A[i, j] with B[j, j:k] row chunk and store the partial product."""
    request_json = request.get_json(silent=True)
    if request_json is None:
        return "Invalid JSON payload", 400
    
    bucket_name = request_json["bucket_name"]

    i, j = request_json["a_position"]
    j_start, j_end = request_json["b_position"]

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Load matrices
    blob_a = bucket.blob(request_json["matrix_a"])
    matrix_bytes = blob_a.download_as_bytes()
    matrix_a = np.load(io.BytesIO(matrix_bytes))

    blob_b = bucket.blob(request_json["matrix_b"])
    matrix_bytes = blob_b.download_as_bytes()
    matrix_b = np.load(io.BytesIO(matrix_bytes))

    # Extract the specific element from A and row chunk from B
    a_value = matrix_a[i, j]
    b_chunk = matrix_b[j, j_start:j_end]
    partial_product = a_value * b_chunk
    
    # Save the result back to storage
    id = request_json["id"]
    result_blob = bucket.blob(f"Map/{i}_{j_start}_{j_end}_{id}.npy")
    result_bytes = io.BytesIO()
    np.save(result_bytes, partial_product)
    result_bytes.seek(0)
    result_blob.upload_from_file(result_bytes, content_type='application/octet-stream')

    return f"Computed partial product for A[{i}, {j}] * B[{j}, {j_start}:{j_end}]", 200