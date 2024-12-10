import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from server_class import Server

def cosine(VM, Servers):
    vm_vec = np.array([v for k, v in VM.items() if k in ['core', 'memory', 'ssd', 'nic']]).reshape(1, -1)

    server_vecs = np.vstack([server.get_server_info(reshape=True) for server in Servers])
    similarities = cosine_similarity(vm_vec, server_vecs).flatten()

    # Filter servers that can accommodate the VM
    valid_indices = [i for i, server_vec in enumerate(server_vecs) if np.all(server_vec >= vm_vec.flatten())]
    if valid_indices:
        best_index = max(valid_indices, key=lambda i: similarities[i])
        Servers[best_index].add_vm(VM)
    else:
        new_server = Server()
        new_server.add_vm(VM)
        Servers.append(new_server)


def cosine_similarity_method(df):
    servers = [Server()]
    # simulate discrete structure where you see each vm one at a time 
    for _, vm in df.iterrows():
        vm = vm.to_dict()
        cosine(vm, servers)


    return len(servers)