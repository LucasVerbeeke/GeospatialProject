"""
@author: Lucas Verbeeke
"""

# This is the necessary Pixel class we need to make the grouping process easier
class Pixel:
    def __init__(self, X, Y, Cluster_value, Group=None):
        self.x = int(X)               # Location x
        self.y = int(Y)               # Location y
        self.cluster = Cluster_value  # Pixel value, which is the value of the cluster after running the classification algorithm
        self.group = Group            # The group it is assigned to
        self.neighbours = []          # The neighbouring pixels in the raster
        self.done = False             # A helping attribute useful for the grouping function

    # Helping function that returns only the neighbours of a pixel that are inside the same cluster (so they have the same pixel value/cluster value)
    def _get_neighbours_in_cluster(self, cluster):
        neighbours = self.neighbours
        for nb in neighbours:
            if nb.cluster != cluster:
                neighbours.remove(nb)
        return neighbours

    # Starting from a pixel in a certain group, this function will assign the same group recursively to all its neighbours within the same cluster
    def _assign_group_to_neighbours(self, cluster, group):
        if self.cluster == cluster and not self.done:
            self.group = group
            self.done = True     # Make sure the pixel won't be considered again
            neighbours = self._get_neighbours_in_cluster(cluster)
            for nb in neighbours:
                nb._assign_group_to_neighbours(cluster, group)