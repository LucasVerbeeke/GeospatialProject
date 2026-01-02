# GeospatialProject

This repository contains the project developed for the **Geospatial Processing** course.  
The project focuses on **raster data analysis**, including **unsupervised classification** of single-band rasters and **conversion of raster groups into vector polygons**.

**Authors:**  
- Ayman Mutasim  
- Lucas Verbeeke  

---

## Project Overview

The project implements two main geospatial processing tasks:

1. **Single-band raster classification** using **K-Means clustering** with an automatic selection of the optimal number of clusters using a **curvature-based elbow (kneedle) method**.
2. **Raster-to-vector conversion**, where all pixels belonging to the same group or class are merged into a single polygon and exported as a **GeoJSON** file.

The implementation is written in Python and uses standard geospatial libraries.

---

## Repository Structure

# GeospatialProject

This repository contains the project developed for the **Geospatial Processing** course.  
The project focuses on **raster data analysis**, including **unsupervised classification** of single-band rasters and **conversion of raster groups into vector polygons**.

**Authors:**  
- Ayman Mutasim  
- Lucas Verbeeke  

---

## Project Overview

The project implements two main geospatial processing tasks:

1. **Single-band raster classification** using **K-Means clustering** with an automatic selection of the optimal number of clusters using a **curvature-based elbow (kneedle) method**.
2. **Raster-to-vector conversion**, where all pixels belonging to the same group or class are merged into a single polygon and exported as a **GeoJSON** file.

The implementation is written in Python and uses standard geospatial libraries.

---

## Repository Structure

GeospatialProject/
│── Data/ # Input raster data (large files usually ignored by git)
│── THE_CREATED_POLYGONS/ # Output GeoJSON polygon files
│── Classification_Function.py # K-Means classification and elbow detection
│── Polygons_From_Groups_Function.py # Raster group to polygon conversion
│── Pixel_Raster_class.py # Helper pixel and raster grouping classes
│── Classification_TEST.ipynb # Notebook for testing raster classification
│── Polygon_From_Group_TEST.ipynb # Notebook for testing polygon creation
│── environment.yml # Conda environment definition
│── requirements.txt # Python dependencies
│── .gitignore
│── README.md
│── LICENSE

---


---

## Raster Classification (K-Means)

The classification workflow operates on **single-band rasters** and includes:

- Flattening raster data for clustering
- Running K-Means for multiple values of K
- Computing SSD (sum of squared distances)
- Selecting the optimal number of clusters using the elbow method
- Producing a classified raster using the cluster centroids

Main functions are implemented in:

- `Classification_Function.py`

Key outputs:
- Cluster labels (2D array)
- Floating-point cluster centroids
- Optimal number of clusters
- Raster metadata for writing outputs

---

## Raster Group to Polygon Conversion

This step converts all raster pixels with the same value into a **single merged polygon**:

- A mask is created for a selected raster value
- Raster pixels are polygonized
- All polygons are merged into one geometry
- The result is exported as a **GeoJSON FeatureCollection**

Main functions are implemented in:

- `Polygons_From_Groups_Function.py`

The output polygons are stored in the `THE_CREATED_POLYGONS/` folder.

---

## Pixel and Raster Helper Classes

The file `Pixel_Raster_class.py` contains helper classes used to represent pixels and manage neighbourhood relationships (including optional diagonal connections). These utilities support raster grouping and analysis logic.

---

## Environment Setup

The project can be run using either Conda or pip.

### Using Conda (recommended)
```bash
conda env create -f environment.yml
conda activate GeosProject

---

Using pip:
pip install -r requirements.txt

---

Running The Project:

+ Use Classification_TEST.ipynb to run and visualize raster classification.
+ Use Polygon_From_Group_TEST.ipynb to convert selected raster groups into polygons.
+ Input raster paths and output locations can be changed directly inside the notebooks.

---

Notes:

+ The classification works only on single-band raster files.
+ Large raster datasets are typically excluded from version control using .gitignore.
+ Output GeoJSON files represent one selected group or class at a time.

---

License:

This project is distributed under the MIT License.
