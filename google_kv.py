from google.cloud import storage
from google.api_core.exceptions import NotFound

 

class GCPBlobKVStore:

    def __init__(self, bucket_name):

        """
        Initialize the GCP Blob Key-Value Store.
        :param bucket_name: Name of the GCP Cloud Storage bucket.

        """
        # The client automatically uses the credentials specified by the
        # GOOGLE_APPLICATION_CREDENTIALS environment variable.

        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

        if not self.bucket.exists():
            raise ValueError(f"Bucket '{bucket_name}' does not exist.")

 

    def set(self, key, value):

        """

        Store a value with the specified key.

 

        :param key: The key (object name).

        :param value: The value (string or bytes).

        """

        blob = self.bucket.blob(key)

        if isinstance(value, str):

            value = value.encode('utf-8')  # Convert string to bytes

        blob.upload_from_string(value)

        # print(f"Set key: '{key}'")

 

    def get(self, key):

        """

        Retrieve the value associated with the specified key.

 

        :param key: The key (object name).

        :return: The value as bytes, or None if key does not exist.

        """

        blob = self.bucket.blob(key)

        try:

            return blob.download_as_bytes()

        except NotFound:

            print(f"Key '{key}' not found.")

            return None

 

    def delete(self, key):

        """

        Delete the key-value pair associated with the specified key.

 

        :param key: The key (object name).

        """

        blob = self.bucket.blob(key)

        blob.delete()

        # print(f"Deleted key: '{key}'")

 

    def exists(self, key):

        """
        Check if a key exists.
        :param key: The key (object name).

        :return: True if exists, False otherwise.

        """

        blob = self.bucket.blob(key)

        return blob.exists()

 

# Example Usage

if __name__ == "__main__":

    # Replace with your actual bucket name
    bucket_name = "jack-fall2024"

    # Initialize the key-value store
    kv_store = GCPBlobKVStore(bucket_name)

    # Set a key-value pair
    kv_store.set("example_key", "This is a sample value.")

    # Get the value
    value = kv_store.get("example_key")
    if value:
        print(f"Retrieved value: {value.decode('utf-8')}")


    # Check if the key exists
    if kv_store.exists("example_key"):
        print("Key 'example_key' exists.")

    # Delete the key
    # kv_store.delete("example_key")


    # Verify deletion
    if not kv_store.exists("example_key"):
        print("Key 'example_key' has been deleted.")