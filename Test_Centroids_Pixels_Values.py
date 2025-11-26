
def show_output_pixel_values(output_path="averaged_test.tif"):
    """
    Loads the classified raster and prints the unique pixel values.
    """
    import rasterio
    import numpy as np
    import os

    # Check if file exists in current folder
    if not os.path.exists(output_path):
        print(f"❌ File not found in current directory: {output_path}")
        print("\n✅ Files in this folder:")
        print(os.listdir())
        return

    with rasterio.open(output_path) as src:
        data = src.read(1)

    unique_vals = np.unique(data)

    print("\n✅ UNIQUE PIXEL VALUES IN OUTPUT RASTER:")
    print(unique_vals)
    print(f"\n✅ Number of classes: {len(unique_vals)}")


# ✅ RUN THIS
show_output_pixel_values()







