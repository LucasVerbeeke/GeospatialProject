"""
@author: Lucas Verbeeke
"""

# This function is necessary to execute before being able to assign groups. It is done automatically in the grouping function, so no need to run it manually
def assign_neighbours_to_raster(raster, shape):
    x_shape, y_shape = shape[1], shape[0]
    for ind, pixel in enumerate(raster):
        neighbours = []
        # Check if the pixel is at the left or right edge of the raster
        if ind%x_shape == 0:
            neighbours.append(raster[ind+1])
        elif ind%x_shape == (x_shape-1):
            neighbours.append(raster[ind-1])
        else:
            neighbours.extend((raster[ind-1], raster[ind+1]))
        # Check if the pixel is at the top or bottom row of the raster
        if ind < x_shape:
            neighbours.append(raster[ind+x_shape])
        elif ind > x_shape*y_shape - x_shape - 1:
            neighbours.append(raster[ind-x_shape])
        else:
            neighbours.extend((raster[ind-x_shape], raster[ind+x_shape]))
        pixel.neighbours = neighbours

# This is the function in which everything comes together. After running this function, all pixels belonging to one cluster will have been assigned to a group.
# To assign a group to every pixel in a raster, you have to apply the function to every cluster
def group_raster(raster, shape, cluster, neighbours_assigned=False):
    if not neighbours_assigned:
        assign_neighbours_to_raster(raster, shape)
    group_count = 1 # This variable keeps track of the number of variables
    # Consider all pixels belonging to the desired cluster and assigning the right group to it and all of its neighbours
    for pixel in raster:
        if pixel.cluster == cluster and not pixel.done:
            pixel.group = group_count
            pixel._assign_group_to_neighbours(cluster, group_count)
            group_count += 1
    # Make sure running the function again will give the same result
    for pixel in raster:
        pixel.done = False
    number_of_groups = group_count - 1
    return number_of_groups

# This function can be executed after the pixels have been assigned to a group. It will return a list of all pixels that belong to a certain group.
def get_pixels_of_group(raster, group):
    pixel_lst = []
    for pixel in raster:
        if pixel.group == group:
            pixel_lst.append(pixel)
    return pixel_lst