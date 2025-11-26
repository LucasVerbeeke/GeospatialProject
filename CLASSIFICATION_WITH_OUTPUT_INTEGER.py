
# By : Ayman Mutasim


import numpy as np
import matplotlib.pyplot as plt
import rasterio

# --- CONFIGURATION & DATA PATHS ---
# 1. CHANGE THIS PATH to your single-band raster file (.tif, .img, etc.)
RASTER_FILE_PATH = "INPUT RASTER FILE PATH"

# 2. Maximum number of clusters to test in the Elbow Method (e.g., 10)
MAX_CLUSTERS_TO_TEST = 10

# 3. CHANGE THIS PATH for the output classified raster file (e.g., .tif)
OUTPUT_RASTER_PATH = "OUTPUT FILE PATH AND NAME"

# --------------------------------------------------------
# 4. CORE K-MEANS LOGIC (Single Band)
# --------------------------------------------------------

def kmeans_single_band(data_2d, k, max_iters=100, tolerance=1e-4, seed=42):
    """ Runs K-Means on a 2D (height, width) array and returns results.
        Centroids are calculated using np.round() for integer output.
    """
    x, y = data_2d.shape
    # Reshape to (N, 1) for K-Means calculation
    reshaped_data = data_2d.reshape(-1, 1)
    num_samples = reshaped_data.shape[0]

    np.random.seed(seed)
    # Initialize centroids as floats, but based on pixel values
    centroids = reshaped_data[np.random.choice(num_samples, k, replace=False)].flatten().astype(np.float64)

    for _ in range(max_iters):
        distances = np.abs(reshaped_data - centroids)
        closest_centroids = np.argmin(distances, axis=1)
        new_centroids = np.zeros(k, dtype=np.float64)

        for i in range(k):
            cluster_points = reshaped_data[closest_centroids == i]
            if cluster_points.size > 0:
                # --- MODIFICATION 1: Round the calculated mean to ensure integer centroids
                # Use float for convergence check, but the value represents the rounded integer center
                new_centroids[i] = np.round(cluster_points.mean())
            else:
                new_centroids[i] = centroids[i]

        if np.all(np.abs(new_centroids - centroids) < tolerance):
            break
        centroids = new_centroids

    # 5. Calculate SSD (Inertia)
    final_distances = np.min(np.abs(reshaped_data - centroids), axis=1)
    ssd = np.sum(final_distances**2)

    segmented_output = closest_centroids.reshape(x, y)

    # --- MODIFICATION : Convert final centroids to integer type (np.int32)
    final_centroids_int = centroids.astype(np.int32)

    return segmented_output, final_centroids_int, ssd

# --------------------------------------------------------
# 6. NEW FUNCTION: SAVE RASTER OUTPUT
# --------------------------------------------------------

def save_classified_raster(output_data, output_path, src_profile):
    """ Writes the classified NumPy array to a GeoTIFF file. """
    print(f"\n--- Saving Classified Raster to: {output_path} ---")

    # Update the profile for the output file
    out_profile = src_profile.copy()
    out_profile.update({
        # dtype is determined by the input array (now np.int32)
        'dtype': output_data.dtype,
        'count': 1,
        'nodata': None
    })

    try:
        with rasterio.open(output_path, 'w', **out_profile) as dst:
            dst.write(output_data, 1) # Write the classified data to band 1
        print("Raster successfully saved!")
    except Exception as e:
        print(f"ERROR saving raster: {e}")

# --------------------------------------------------------
# 7. MAIN CLASSIFICATION WORKFLOW (WITH SAVING)
# --------------------------------------------------------

def classify_single_band_raster(file_path, max_k=10, output_path=None):
    """
    Reads a single-band raster, determines optimal K via Elbow Method,
    classifies the data, and plots the results, AND SAVES THE RASTER.
    """
    # --- STEP 1: LOAD AND PREPARE DATA (SIMPLIFIED) ---

    with rasterio.open(file_path) as src:
        if src.count != 1:
            print(f"ERROR: Raster must have 1 band, found {src.count}. Skipping.")
            return

        # Store the metadata (profile) for later saving
        src_profile = src.profile

        # Read data directly as float64 (to avoid integer overflow/underflow during math)
        data = src.read(1).astype(np.float64)

        # All pixels are considered valid data and flattened for clustering
        valid_data = data.flatten()

        if valid_data.size == 0:
            print("ERROR: No data found in the raster.")
            return

        print(f"Data Loaded: {file_path.split('/')[-1]}. Shape: {data.shape}")

    # --- STEP 2: ELBOW METHOD (Find Optimal K) ---
    ssd_scores = []
    k_range = range(1, max_k + 1)

    print("--- Running Elbow Method to find optimal K ---")
    for k in k_range:
        if k == 1:
            mean_value = np.mean(valid_data)
            ssd = np.sum((valid_data - mean_value)**2)
        else:
            # Run K-Means on the valid_data (reshaped to N, 1)
            # Use data.copy() to ensure valid_data is not modified by np.round() during elbow test
            _, _, ssd = kmeans_single_band(data.copy(), k)

        ssd_scores.append(ssd)
        print(f"Calculated SSD for K={k}: {ssd:.4f}")

    # --- SIMPLIFIED ELBOW HEURISTIC (NumPy only) ---
    first_diff = np.diff(ssd_scores)
    second_diff = np.diff(first_diff)

    if second_diff.size > 0:
        optimal_k_index = np.argmin(second_diff)
        optimal_k = optimal_k_index + 2
    else:
        optimal_k = max_k

    print(f"\nCalculated Optimal K (Elbow Point Heuristic): K = {optimal_k}")

    # Plotting the Elbow Curve
    plt.figure(figsize=(8, 5))
    plt.plot(k_range, ssd_scores, marker='o', linestyle='--')
    plt.plot(optimal_k, ssd_scores[optimal_k - 1], 'ro', markersize=10, label=f'Optimal K = {optimal_k}')
    plt.title('Elbow Method: Optimal K Selection (Heuristic)')
    plt.xlabel('Number of Clusters (K)')
    plt.ylabel('Sum of Squared Distances (SSD / Inertia)')
    plt.xticks(k_range)
    plt.legend()
    plt.grid(True)
    plt.show()

    # --- STEP 3: FINAL CLASSIFICATION & SAVING ---

    # Run K-Means with the optimal K - final_centroids are now np.int32
    segmented_labels_1d, final_centroids, _ = kmeans_single_band(data, optimal_k)

    print("\n--- Final Classification Results ---")
    print(f"Final Centroids (Integer Values) for K={optimal_k}: {final_centroids}")

    # 1. Map the cluster labels (0, 1, 2, ...) back to their corresponding integer centroid values
    # Initialize the output array with integer type (np.int32)
    classified_pixel_values = np.zeros(data.size, dtype=np.int32)
    for i in range(optimal_k):
        # Find all pixels belonging to cluster 'i' and assign the integer centroid value
        classified_pixel_values[segmented_labels_1d.flatten() == i] = final_centroids[i]

    # 2. Reshape the 1D classified array back to the original 2D image shape
    classified_raster_data = classified_pixel_values.reshape(data.shape)

    # 3. Explicitly ensure the output raster data type is integer
    # --- MODIFICATION 3: Explicitly set the data type to np.int32
    classified_raster_data = classified_raster_data.astype(np.int32)

    # 4. Save the resulting raster file
    if output_path:
        save_classified_raster(classified_raster_data, output_path, src_profile)

    # --- STEP 4: PLOTTING THE SEGMENTED IMAGE (using the original labels for better visual separation) ---
    segmented_output_full = segmented_labels_1d.reshape(data.shape).astype(np.float64)

    plt.figure(figsize=(10, 8))
    img = plt.imshow(segmented_output_full, cmap='nipy_spectral', vmin=0, vmax=optimal_k - 1)

    plt.colorbar(img, ticks=np.arange(optimal_k), label=f'Cluster Label (0 to {optimal_k-1})')
    plt.title(f'K-Means Segmentation (Optimal K={optimal_k}) - Visual Labels')
    plt.xlabel('Column Index')
    plt.ylabel('Row Index')
    plt.grid(color='white', linestyle='-', linewidth=0.5)

    plt.show()

# ==========================================================
# 8. USAGE: EXECUTE THE WORKFLOW
# ==========================================================

# Run the entire classification workflow
classify_single_band_raster(RASTER_FILE_PATH, MAX_CLUSTERS_TO_TEST, OUTPUT_RASTER_PATH)







