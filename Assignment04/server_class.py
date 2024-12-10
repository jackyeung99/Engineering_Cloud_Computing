import numpy as np

class Server:
    def __init__(self, cores=1.0, memory=1.0, ssd=1.0, nic=1.0):
        self.vm_list = []
        self.cores = cores
        self.memory = memory 
        self.ssd = ssd 
        self.nic = nic

    def add_vm(self, vm):
        self.vm_list.append(vm['vmId'])
        self.cores -= vm['core']
        self.memory -= vm['memory']
        self.ssd -= vm['ssd']
        self.nic -= vm['nic']

    def get_server_info(self, reshape=True):
        info = np.array([self.cores, self.memory, self.ssd, self.nic])
        return info.reshape(1, -1) if reshape else info
    
    def display_server_info(self):
        print(f"""SERVER CAPACITY:
        CORES: {self.cores}
        MEMORY: {self.memory}
        SSD: {self.ssd}
        NIC: {self.nic}""")
