"""
@author: Lucas Verbeeke
"""

import numpy as np

class Raster:
    def __init__(self, lst, shape, groups=[], neighbours_diagonal=False):
        self.lst = lst                       # The list with all pixels, they need to be actual pixel objects
        self.group_sizes = groups            # A list with the sizes of all groups
        self.n_groups = len(groups)          # The number of current groups
        self.group_counter = len(groups)     # The highest group number, only interesting inside the grouping function
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

    # This is the function in which everything comes together
    # After running this function, all pixels belonging to one cluster will have been assigned to a group
    # For every pixel, it looks at the groups of its neighbours and assigns it to the largest group of those
    # Then it will change the groups of the other neighbours to make sure they are in the same group
    def _group_raster(self, cluster):
        for pixel in self.lst:
            if pixel.cluster == cluster and pixel.group is None:
                neighbours = pixel._get_neighbours_in_cluster(cluster) # This makes sure only neighbours inside the same cluster are considered
                nb_group_lst = []
                for nb in neighbours:
                    if nb.group is not None:
                        nb_group_lst.append(nb.group)
                unique_lst = list(set(nb_group_lst))
                nb_groups_unique = len(unique_lst)
                if nb_groups_unique == 0: # No neighbour has already been placed into a group, so we create a new group
                    pixel.group = self.group_counter
                    self.n_groups += 1
                    self.group_counter += 1
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
                    # Add current pixel to largest group
                    pixel.group = max_group
                    self.group_sizes[pixel.group] += 1
                    unique_lst.remove(max_group)
                    # Change all pixels from the smaller groups to the largest, which essentially merges all neighbouring groups
                    for pixel2 in self.lst:
                        if pixel2.group is not None and pixel2.group in unique_lst:
                            self.group_sizes[pixel2.group] -= 1
                            pixel2.group = max_group
                            self.group_sizes[max_group] += 1
                    for group in unique_lst:
                        if self.group_sizes[group] == 0:
                            self.n_groups -= 1
                        else:
                            print("Something went wrong. Group should be empty, but group " + str(group) + " size is " + str(self.group_sizes[group])) #Built-in message to check whether everything is working properly
        return self.n_groups, self.group_counter, self.group_sizes

    # This function makes sure that all the empty groups are removed from the group_sizes list, while still all pixels have the correct group
    def _remove_empty_groups(self):
        empty_groups = [] # This list stores all the groups that are empty
        for group, group_size in enumerate(self.group_sizes):
            if group_size == 0:
                empty_groups.append(group)
        decrease_lst = [] # This list will contain the number of places a group is shifted down in the list
        # This loop looks at how many empty groups exist before each non-empty group
        for group in range(self.group_counter):
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
        for group in range(self.group_counter):
            shift = decrease_lst[group]
            if shift >= 1:
                self.group_sizes[group-shift] = self.group_sizes[group]
                self.group_sizes[group] = 0
        # All empty groups should now be at the end of the group sizes list. They are removed from the list below
        self.group_sizes = [size for size in self.group_sizes if size != 0]
        self.group_counter = self.n_groups
        return self.group_sizes
    
    # This function can be executed after the pixels have been assigned to a group. It will return a list of all pixels that belong to a certain group.
    def _get_pixels_of_group(self, group):
        pixel_lst = []
        for pixel in self.lst:
            if pixel.group == group:
                pixel_lst.append(pixel)
        return pixel_lst

    # This function creates a 2D-array where all entries are the groups of the pixels if they have one, otherwise it's still the cluster they are in. It can be used in the process of creating a raster datatype, from where the groups can be changed into polygons
    def _create_raster_array(self):
        res_array = np.zeros((self.y_shape, self.x_shape))
        for pixel in self.lst:
            if pixel.group is not None:
                res_array[pixel.y, pixel.x] = pixel.group
            else:
                res_array[pixel.y, pixel.x] = pixel.cluster
        return res_array