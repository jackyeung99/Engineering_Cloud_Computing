from pymemcache.client.base import Client



if __name__ == '__main__':
    client = Client(('localhost', 9889))

    # First, use the 'set' command
    set_response = client.set('mem_cache', 'mem_value', noreply=True)
    print(f"SET Response: {set_response}")

    # Now, retrieve the value using 'get'
    get_response = client.get('mem_cache',  noreply=True)
    print(f"GET Response: {get_response.decode('utf-8') if get_response else 'Key not found'}")