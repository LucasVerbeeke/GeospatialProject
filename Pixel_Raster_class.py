"""
@author: Lucas Verbeeke
"""

import numpy as np
import rasterio

# This is the necessary Pixel class we need in order to make the grouping process easier
class Pixel:
    def __init__(self, X, Y, Cluster_value, Group=None):
        self.x = int(X)               # Location x
        self.y = int(Y)               # Location y
        self.cluster = Cluster_value  # Pixel value, which is the value of the cluster after running the classification algorithm
        self.group = Group            # The group it is assigned to
        self.neighbours = []          # The neighbouring pixels in the raster


# This is the Raster class containing all important functions
class Raster:
    def __init__(self, lst, shape, groups=[], neighbours_diagonal=False):
        self.lst = lst                       # The list with all pixels, they need to be actual pixel objects
        self.group_sizes = groups            # A list with the sizes of all groups
        self.n_groups = len(groups)          # The number of current groups
        self.groups_per_cluster = {}         # A dictionary with cluster values as keys and the group indices belonging to the cluster as values
        self.x_shape = shape[1]              # The width of the raster
        self.y_shape = shape[0]              # The height of the raster

        # The following loop makes sure all pixels in the raster have their neighbours listed correctly
        for ind, pixel in enumerate(self.lst):
            neighbours = []
            if neighbours_diagonal: #Neighbours are also diagonal
                # Checks if the pixel is at the left or right edge of the raster
                if ind%self.x_shape == 0:
                    left = True
                    right = False
                    neighbours.append(self.lst[ind+1])
                elif ind%self.x_shape == (self.x_shape-1):
                    right = True
                    left = False
                    neighbours.append(self.lst[ind-1])
                else:
                    left, right = False, False
                    neighbours.extend((self.lst[ind-1], self.lst[ind+1]))
                # Checks if the pixel is at the top or bottom row of the raster
                # It also checks which diagonal neighbours it should add based on the position in the grid
                if ind < self.x_shape:
                    neighbours.append(self.lst[ind+self.x_shape])
                    if left:
                        neighbours.append(self.lst[ind+self.x_shape+1])
                    elif right:
                        neighbours.append(self.lst[ind+self.x_shape-1])
                    else:
                        neighbours.extend((self.lst[ind+self.x_shape-1], self.lst[ind+self.x_shape+1]))
                elif ind > self.x_shape*self.y_shape - self.x_shape - 1:
                    neighbours.append(self.lst[ind-self.x_shape])
                    if left:
                        neighbours.append(self.lst[ind-self.x_shape+1])
                    elif right:
                        neighbours.append(self.lst[ind-self.x_shape-1])
                    else:
                        neighbours.extend((self.lst[ind-self.x_shape-1], self.lst[ind-self.x_shape+1]))
                else:
                    neighbours.extend((self.lst[ind-self.x_shape], self.lst[ind+self.x_shape]))
                    if left:
                        neighbours.extend((self.lst[ind+self.x_shape+1], self.lst[ind-self.x_shape+1]))
                    elif right:
                        neighbours.extend((self.lst[ind+self.x_shape-1], self.lst[ind-self.x_shape-1]))
                    else:
                        neighbours.extend((self.lst[ind+self.x_shape-1], self.lst[ind+self.x_shape+1], self.lst[ind-self.x_shape+1], self.lst[ind-self.x_shape-1]))
                pixel.neighbours = neighbours
            else: #Neighbours are not diagonal
                # Checks if the pixel is at the left or right edge of the raster
                if ind%self.x_shape == 0:
                    neighbours.append(self.lst[ind+1])
                elif ind%self.x_shape == (self.x_shape-1):
                    neighbours.append(self.lst[ind-1])
                else:
                    neighbours.extend((self.lst[ind-1], self.lst[ind+1]))
                # Checks if the pixel is at the top or bottom row of the raster
                if ind < self.x_shape:
                    neighbours.append(self.lst[ind+self.x_shape])
                elif ind > self.x_shape*self.y_shape - self.x_shape - 1:
                    neighbours.append(self.lst[ind-self.x_shape])
                else:
                    neighbours.extend((self.lst[ind-self.x_shape], self.lst[ind+self.x_shape]))
                pixel.neighbours = neighbours

    # For every pixel, it looks at the groups of its neighbours and assigns it to the largest group of those
    # The groups of the other neighbours are then stored in a dictionary
    # At the end those groups of the other neighbours are changed to make sure they are in the correct group
    def _group_raster(self, cluster):
        removed_groups_dict = {} # This dictionary will be used later
        for pixel in self.lst:
            if abs(pixel.cluster - cluster) < 1e-5 and pixel.group is None:
                neighbours = pixel.neighbours # Get all neighbours of the pixel
                nb_group_lst = []
                for nb in neighbours:
                    if nb.group is not None and abs(nb.cluster - cluster) < 1e-5:  # This makes sure only neighbours with an already assigned group inside the same cluster are considered
                        nb_group_lst.append(nb.group)
                unique_lst = list(set(nb_group_lst))
                nb_groups_unique = len(unique_lst) # Number of neighbours in different groups
                if nb_groups_unique == 0: # No neighbour has already been placed into a group, so we create a new group
                    pixel.group = self.n_groups
                    self.n_groups += 1
                    self.group_sizes.append(1)
                elif nb_groups_unique == 1: # All neighbours are within the same group, so the current pixel is added to that one
                    cur_group = nb_group_lst[0]
                    pixel.group = cur_group
                    self.group_sizes[cur_group] += 1
                else: # Neighbours are in two or more (probably only two) different groups
                    max_groupsize = 0
                    max_group = None
                    # Find out which neighbouring group is largest in size
                    for group in unique_lst:
                        groupsize = self.group_sizes[group]
                        if groupsize > max_groupsize:
                            max_groupsize = groupsize
                            max_group = group
                    unique_lst.remove(max_group) # Remove this largest neighbouring group from the list of groups that need to be changed
                    destination_group = max_group
                    # This loop makes sure the dictionary doesn't get too many cross references by checking whether the destination itself already has a
                    # destination in the dictionary
                    while destination_group in removed_groups_dict.keys():
                        destination_group = removed_groups_dict.get(destination_group) 
                    # This loop makes sure all groups that are not the max_group will be mapped to the destination group
                    for rest_group in unique_lst:
                        if rest_group not in removed_groups_dict and rest_group != destination_group:
                            removed_groups_dict[rest_group] = destination_group
                    # Add current pixel to the destination group
                    pixel.group = destination_group
                    self.group_sizes[destination_group] += 1
        moved = 1
        # All pixels in a group that needs to be cleared (because it was not the largest in a comparison in the previous step) will be put a group according
        # to the created dictionary. This is repeated until all pixels are in the correct group. At that point no pixel will be moved to another group, so
        # the loop won't be executed again
        while moved > 0:
            moved = 0
            for pixel in self.lst:
                if pixel.group in removed_groups_dict:
                    old_group = pixel.group
                    new_group = removed_groups_dict.get(old_group)
                    pixel.group = new_group
                    self.group_sizes[old_group] -= 1
                    self.group_sizes[new_group] += 1
                    moved += 1
        removed_groups_dict = {}
        return self.n_groups, self.group_sizes

    # This function makes sure that all the empty groups are removed from the group_sizes list, while still all pixels have the correct group
    def _remove_empty_groups(self):
        empty_groups = [] # This list stores all the groups that are empty
        for group, group_size in enumerate(self.group_sizes):
            if group_size == 0:
                empty_groups.append(group)
        decrease_lst = [] # This list will contain the number of places a group is shifted down in the list
        # This loop looks at how many empty groups exist before each non-empty group
        for group in range(self.n_groups):
            shift = 0
            if group not in empty_groups:
                for empty_group in empty_groups:
                    if empty_group < group:
                        shift += 1
                    else:
                        break
            decrease_lst.append(shift)
        # This loop makes sure that all pixels have again the correct group assigned
        for pixel in self.lst:
            group = pixel.group
            if group is not None:
                pixel.group = group - decrease_lst[group]
        # This loop makes sure that the group sizes are stored correctly
        for group in range(self.n_groups):
            shift = decrease_lst[group]
            if shift >= 1:
                self.group_sizes[group-shift] = self.group_sizes[group]
                self.group_sizes[group] = 0
        # All empty groups should now be at the end of the group sizes list. They are removed from the list below
        self.group_sizes = [size for size in self.group_sizes if size != 0]
        self.n_groups = len(self.group_sizes)
        return self.n_groups, self.group_sizes

    # The only thing this function does is executing both the _group_raster function and the _remove_empty_groups function at once
    def _grouping_process(self, cluster):
        already_existing_groups = self.n_groups
        self._group_raster(cluster)
        self._remove_empty_groups()
        self.groups_per_cluster[cluster] = (already_existing_groups, self.n_groups-1) # This keeps track of which groups are from this cluster
        return self.n_groups, self.group_sizes

    # This function creates a 2D-array where all entries are the groups of the pixels if they have one, otherwise it's still the cluster they are in. It is
    # used in the process of creating a raster datatype
    def _create_raster_array(self):
        res_array = np.zeros((self.y_shape, self.x_shape))
        for pixel in self.lst:
            if pixel.group is not None:
                res_array[pixel.y, pixel.x] = pixel.group
            else:
                res_array[pixel.y, pixel.x] = pixel.cluster
        return res_array

    # With this function, a raster data type is saved with the assigned groups as pixel values. From here the groups can be changed into polygons
    def _output_raster(self, output_path, CRS):
        array = self._create_raster_array()
        # Define georeferencing info
        pixel_size = 1.0  # size of pixel in map units
        x_min, y_max = 0.0, self.y_shape  # top-left corner coordinates
        
        transform = rasterio.transform.from_origin(x_min, y_max, pixel_size, pixel_size)
        
        # Write raster
        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            height=array.shape[0],
            width=array.shape[1],
            count=1,               # number of bands
            dtype=array.dtype,
            crs=CRS,
            transform=transform
        ) as dst:
            dst.write(array, 1)