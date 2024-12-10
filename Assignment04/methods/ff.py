from server_class import Server
import numpy as np 

def ff(VM, Servers):
    vm_vec = np.array([v for k, v in VM.items() if k in ['core', 'memory', 'ssd', 'nic']]).reshape(1, -1)

    for server in Servers:
        server_vec = np.array(server.get_server_info()).reshape(1, -1)
        if np.all(server_vec.flatten() >= vm_vec.flatten()):
            server.add_vm(VM)
            return 

    new_server = Server()
    new_server.add_vm(VM)
    Servers.append(new_server)


def ff_method(df):
    servers = [Server()]
    # simulate discrete structure where you see each vm one at a time 
    for _, vm in df.iterrows():
        vm = vm.to_dict()
        ff(vm, servers)


    return len(servers)
