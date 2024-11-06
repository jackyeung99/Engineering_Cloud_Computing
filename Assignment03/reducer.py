import numpy as np
from google.cloud import storage
import io

def reduce_function(request):
   
    request_json = request.get_json(silent=True)
    bucket_name = request_json["bucket_name"]
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    final_result = None

    # Iterate over the provided file list and sum their contents
    for file in request_json['files']:
        blob = bucket.blob(file)
        matrix_bytes = blob.download_as_bytes()
        matrix_chunk = np.load(io.BytesIO(matrix_bytes), allow_pickle=True)
        
        if final_result is None:
            final_result = matrix_chunk
        else:
            final_result += matrix_chunk


    # Save the result back to the bucket
    result_blob = bucket.blob(f"Reduce/{request_json['i']}_{request_json['j']}_{request_json['j_end']}.npy")
    result_bytes = io.BytesIO()
    np.save(result_bytes, final_result)
    result_bytes.seek(0)
    result_blob.upload_from_file(result_bytes, content_type='application/octet-stream')

    return f"Computed final product", 200


