# By: Ayman Mutasim

import rasterio
from shapely.geometry import box, mapping
from shapely.ops import unary_union
import numpy as np
import json


# --------------------------------------------------------
# RASTER GROUP → POLYGON
# --------------------------------------------------------
def raster_group_to_polygon(raster_path, target_value):
    """
    Converts all pixels with the same value into a single polygon.

    Parameters
    ----------
    raster_path : str
        Path to input raster
    target_value : float or int
        Pixel value representing the group

    Returns
    -------
    shapely.geometry.Polygon or MultiPolygon
    """

    with rasterio.open(raster_path) as src:
        data = src.read(1)
        transform = src.transform

    mask = data == target_value

    if not np.any(mask):
        raise ValueError(f"No pixels found with value {target_value}")

    rows, cols = np.where(mask) # Get the coordinates of all pixels within the group

    polygons = []
    for r, c in zip(rows, cols):
        x_min, y_max = transform * (c, r)
        x_max, y_min = transform * (c + 1, r + 1)
    
        polygons.append(box(x_min, y_min, x_max, y_max))

    n_pixel = len(polygons)
    merged_polygon = unary_union(polygons)
    return merged_polygon, n_pixel


# --------------------------------------------------------
# SAVE POLYGON AS GEOJSON
# --------------------------------------------------------
def save_polygon_geojson(polygon, output_path, class_value):
    """
    Saves polygon geometry to a GeoJSON file.
    """

    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": mapping(polygon),
            "properties": {
                "class_value": int(class_value) # To make sure it is not np.int64
            }
        }]
    }

    with open(output_path, "w") as f:
        json.dump(geojson, f, indent=2)

    print("GeoJSON saved")

