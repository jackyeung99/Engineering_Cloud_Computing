from server_class import Server
import numpy as np 
from sklearn.cluster import KMeans

class OnlineHarmonic4D:
    def __init__(self, df):
        self.bins = {}
        self.thresholds = self.clustering_based_thresholds(df)
        # self.thresholds = self.compute_quartiles(df)

    def clustering_based_thresholds(self, training, n_clusters=8):
        df = training[['core', 'memory', 'ssd', 'nic']]
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(df)
        thresholds = {i: np.max(cluster, axis=0) for i, cluster in enumerate(kmeans.cluster_centers_)}
        return thresholds

    def partition(self, VM):
        vm_vec = np.array([VM[k] for k in ['core', 'memory', 'ssd', 'nic']])
        distances = {
            cluster_id: np.linalg.norm(vm_vec - center)
            for cluster_id, center in self.thresholds.items()
        }
        best_cluster = min(distances, key=distances.get)
        return best_cluster
    

    def add_item(self, VM):
        subregion = self.partition(VM)

        if subregion not in self.bins:
            self.bins[subregion] = []

        vm_vec = np.array([v for k, v in VM.items() if k in ['core', 'memory', 'ssd', 'nic']])
        for server in self.bins[subregion]:
            if np.all(server.get_server_info(reshape=False) >= vm_vec.flatten()):
                server.add_vm(VM)
                return


        new_bin = Server()
        new_bin.add_vm(VM)
        self.bins[subregion].append(new_bin)

    def count_bins(self):
        """Count total bins used across all subregions."""
        return sum(len(bins) for bins in self.bins.values())
    

def harmonic_method(df, random_sample):
    # undert the assumptiobn you have previous data from training 
    # calculate thresholds for harmonic methods based off simulated training data
    harmonic_bins = OnlineHarmonic4D(random_sample)
    # simulate discrete structure where you see each vm one at a time 
    for _, vm in df.iterrows():
        vm = vm.to_dict()
        harmonic_bins.add_item(vm)

    return harmonic_bins.count_bins()


def get_partitions(df):
    df = df[['core', 'memory', 'ssd', 'nic']]
    print(df.describe())

