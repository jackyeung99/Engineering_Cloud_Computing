import argparse
import pandas as pd
import sqlite3
import sys

class Server:
    def __init__(self, cores, memory, ssd, nic):
        self.vm_list = []
        self.cores = cores
        self.memory = memory 
        self.ssd = ssd 
        self.nic = nic

    def add_vm(self, vm):
        self.vm_list.append(vm)
        self.cores -= vm['cores']
        self.memory -= vm['memory']
        self.ssd -= vm['ssd']
        self.nic -= vm['nic']

    def get_server_info(self):
        return self.cores, self.memory, self.ssd, self.nic
    
    def display_server_info(self):
        print(f"""SERVER CAPACITY:
        CORES: {self.cores}
        MEMORY: {self.memory}
        SSD: {self.ssd}
        NIC: {self.nic}""")

def save_vm_data():
    c = sqlite3.connect('Data/packing_trace_zone_a_v1.sqlite')
    q = '''
        SELECT
            vm.vmid,
            vm.starttime,
            vm.endtime,
            unique_vmType.core,
            unique_vmType.memory,
            unique_vmType.ssd,
            unique_vmType.nic

        FROM 
            vm 
        JOIN 
            (
                SELECT DISTINCT vmTypeId, core, memory, ssd, nic
                FROM vmType
            ) AS unique_vmType 
        ON 
            vm.vmTypeId = unique_vmType.vmTypeId
        LIMIT
            100000;
        '''
    df = pd.read_sql_query(q, c)
    # df = df.drop_duplicates(subset=['vmTypeId'], keep='first')
    df.to_csv('Data/vm_info.csv')

# packing methods
def cosine(vm):
    pass

def ffd(vm):
    pass


# Server assignment 
def assign_vms(vm_info, policy='cosine'):
    server_counter = 0
    server = Server()

    # simulate discrete structure where you see each vm one at a time 
    for vm in vm_info.sort_values(by=['starttime']).iterrows():

        if policy == 'cosine':
            cosine(vm)
        elif policy == 'ffd':
            ffd(vm)

        print(vm)
        break

    return server_counter




def main():
    parser = argparse.ArgumentParser(description="Process some input arguments.")
    parser.add_argument('--policy', type=str, required=True, help="Policy to use, e.g., ffd.")
    parser.add_argument('--numvms', type=int, required=True, help="Number of VMs to process.")
    args = parser.parse_args()
 
    policy = args.policy
    num_vms = args.numvms

    # save_vm_data()
    df = pd.read_csv('Data/vm_info.csv')[:num_vms]
    M = assign_vms(df, policy)
    print(f"NUMBER OF SERVERS REQUIRED: {M}")



if __name__ == '__main__':
    main()
