# By: Ayman Mutasim

import rasterio
from rasterio import features
from shapely.geometry import shape, mapping
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

    shapes_generator = features.shapes(
        mask.astype(np.uint8),
        mask=mask,
        transform=transform
    )

    polygons = [
        shape(geom)
        for geom, value in shapes_generator
        if value == 1
    ]

    merged_polygon = unary_union(polygons)

    return merged_polygon


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
                "class_value": class_value
            }
        }]
    }

    with open(output_path, "w") as f:
        json.dump(geojson, f, indent=2)

