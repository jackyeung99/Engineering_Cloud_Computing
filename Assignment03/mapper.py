import numpy as np
from google.cloud import storage
import io

def map_matrix_multiplication(request):
    """Map function to multiply A[i, j] with B[j, j:k] row chunk and return the partial product."""
    request_json = request.get_json(silent=True)
    if request_json is None:
        return "Invalid JSON payload", 400

    # Extract details from the request payload
    matrix_a_chunk = int(request_json["matrix_a_chunk"])
    matrix_b_chunk = np.array(request_json["matrix_b_chunk"])


    partial_product = matrix_a_chunk * matrix_b_chunk

    return partial_product.tolist(), 200