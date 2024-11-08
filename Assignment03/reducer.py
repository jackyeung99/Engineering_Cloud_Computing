import numpy as np
from google.cloud import storage
import io



def reduce_function(request):
    """Reduce function to sum partial products and return the final result."""
    request_json = request.get_json(silent=True)
    if request_json is None:
        return "Invalid JSON payload", 400

    partial_results = [np.array(chunk) for chunk in request_json["partial_results"]]

    final_result = np.sum(partial_results, axis=0)

    return final_result.tolist(), 200
