# GeospatialProject

This repository contains the project developed for the Geospatial Processing course.  
The project focuses on raster data analysis, including unsupervised classification of single-band raster, the grouping of connected regions of the same cluster and the conversion of those groups into vector polygons.

**Authors:**  
- Ayman Mutasim  
- Lucas Verbeeke  

---

## Project Overview

The project implements three main geospatial processing tasks:

1. **Single-band raster classification** using K-Means clustering with an automatic selection of the optimal number of clusters using a curvature-based elbow (kneedle) method.
2. **Grouping connected regions**, where all connected pixels belonging to the same cluster are merged. into a single polygon and exported as a GeoJSON file.
3. **Creating polygons from the groups** The groups from the previous step are transformed into polygons and exported as a GeoJSON file.

   ## Workflow Overview

```mermaid
flowchart TD
  A[Input: Single-band raster (.tif)] --> B[K-Means Classification<br/>(kneedle elbow for optimal K)]
  B --> C[Classified Raster<br/>(cluster labels)]
  C --> D[Group Connected Regions<br/>(same label + neighbors)]
  D --> E[Groups Raster<br/>(unique id per region)]
  E --> F[Create Polygons]
  F --> G[Output: GeoJSON (polygons)]
```


The steps are described in more detail below.

### Raster Classification (K-Means)

This step is implemented in the file Classification_Function.py. It is based on the implementation of the clustering algorithm in class. The classification workflow operates on **single-band rasters**. The steps taken in the process are the following:
- Flattening raster data for clustering
- Running K-Means clustering for multiple values of K
- Computing SSD (sum of squared distances) for all these values
- Selecting the optimal number of clusters using the elbow method
- Producing a classified raster using the optimal k value
- Giving the centroids of the clusters as output
- The newly classified raster is stored in a directory of your choice.

### Group creation

The grouping process is implemented in the file Pixel_Raster_class.py. The following steps are taken in the process:

- For all pixels in the raster a pixel object from the implemented Pixel class is created.
- These pixels objects are used in the creation of a raster object of the Raster class. Automatically the neighbours of all pixels are stored in this step. It is possible to choose if neighbours are also diagonal. By default, this is not the case.
- The connected groups for one cluster are created, looping through all pixels of the raster. It assigns the same groups to a pixel as the largest group of its neighbours, if they are already grouped.
- If a pixel's neighbours have different groups, the groups are merged.
- At the end, the groups are cleaned up, because the merging process leaves empty groups behind.
- A new single-band raster is given as output. Here, every group has its own pixel value. It can be saved in a directory of your choice.

### Groups to polygons

The polygon creation is implemented in the file Polygons_From_Groups_Function.py. The following steps are taken in the process:

- A group to create its polygon of, needs to be manually chosen.
- Every pixels from that groups is converted to a one-by-one polygon.
- All these boxes are merged.
- The result is exported as a GeoJSON FeatureCollection.

---

## Testing and Using the library

### Environment Setup

After downloading the github repository on your local computer, the right packages need to be installed in your virtual environment. This can be done either with Conda or with Pip.

**Using Conda**
Run in the Anaconda Powershell Prompt the following lines:
```bash
conda env create -f environment.yml
conda activate GeosProject
```
If you run the library in this environment it should 

**Using Pip**
Run in the Powershell of your choice the following line:
```bash
pip install -r requirements.txt
```

### Running the test files

Now the test files can be executed to see how the library works and to verify it. The files Test_Amsterdam, Test_Khartoum and Test_Belgium use a raster of the mentioned regions and show how the library works. The corresponding tif files can be found in the 'Data' folder. Here, the resulting tif files are also stored. The resulting GeoJSON file is stored in the 'THE_CREATED_POLYGONS' folder. Note that especially the notebooks can take several minutes to execute (especially the Amsterdam one). Also, in the Belgium file, the elbow-method selected 2 clusters as the optimal number of clusters. This looks like it is not the best number of clusters, but that is likely because this is determined numerically. There are different ways of selecting the right number of clusters and that can depend on the original data file. Apparently, for the Belgium one, this is not the ideal method.

### Using the library

If one wants to use the developed functions in this library, the lay-out of the test files can be used. Here, the filepaths need to be changed to your own data file. Besides that, if one wants to create the polygon of a different group, the target_group number needs to be changed. It is also possible to decide that diagonal pixels are also considered neighbours.
A raster object contains the attribute groups_per_cluster, which shows which groups belong to which cluster centroid. The group sizes can be viewed with the group_sizes attribute and the total number of groups with the attribute n_groups.

### Contributing to the library

An extension to this library could be the addition of creating polygons for all groups automatically. It might also be useful to store the cluster centroid value directly with the group number. This makes sure the right interpretation of a certain group can be made.

---

Additional notes:

- The classification works only on single-band raster files.
- For large raster files, it can take several minutes to execute the code.
- Output GeoJSON files represent one selected group or class at a time.

---

License:

This project is distributed under the MIT License.
