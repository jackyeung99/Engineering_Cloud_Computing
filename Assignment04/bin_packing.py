import argparse
import pandas as pd
import sqlite3
import sys
import numpy as np

from methods.cosine import cosine_similarity_method
from methods.ff import ff_method
from methods.harmonic import harmonic_method, get_partitions


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


# Server assignment 
def assign_vms(df, policy, random_sample):
    M = None
    if policy == 'cosine':
        M = cosine_similarity_method(df)
    elif policy == 'ff':
        M = ff_method(df)    
    elif policy == 'harmonic':
        M = harmonic_method(df, random_sample)

    return M


def main():
    parser = argparse.ArgumentParser(description="Process some input arguments.")
    parser.add_argument('--policy', type=str, required=True, help="Policy to use, e.g., ffd.")
    parser.add_argument('--numvms', type=int, required=True, help="Number of VMs to process.")
    args = parser.parse_args()
 
    policy = args.policy
    num_vms = args.numvms
    
    # save_vm_data()

    df = pd.read_csv('Data/vm_info.csv').sort_values(by=['starttime'])
    # random_sample = df.sample(10000)
    random_sample = df[:10000]
    df = df[:num_vms]
    M = assign_vms(df, policy, random_sample)
    print(f"Policy: {policy}")
    print(f"NUMBER OF SERVERS REQUIRED: {M}")



if __name__ == '__main__':
    main()
