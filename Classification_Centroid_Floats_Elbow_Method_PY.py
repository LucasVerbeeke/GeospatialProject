# By : Ayman Mutasim

import numpy as np
import rasterio


# --------------------------------------------------------
# PRINT CENTROIDS
# --------------------------------------------------------
def show_cluster_centroids(centroids):
    """
    Prints the final K-means centroids.
    """
    print("\nFINAL FLOAT CENTROIDS FROM K-MEANS:")
    print(np.array(centroids))
    print(f"\nNumber of centroids: {len(centroids)}")


# --------------------------------------------------------
# K-MEANS (FLOAT CENTROIDS)
# --------------------------------------------------------
def kmeans_single_band(data_2d, k, max_iters=100, tolerance=1e-4, seed=42):
    """
    Performs K-means clustering on a single-band raster array.
    """
    x, y = data_2d.shape
    reshaped = data_2d.reshape(-1, 1)

    np.random.seed(seed)
    centroids = reshaped[
        np.random.choice(reshaped.shape[0], k, replace=False)
    ].flatten().astype(float)

    for _ in range(max_iters):
        distances = np.abs(reshaped - centroids)
        closest = np.argmin(distances, axis=1)

        new_centroids = np.zeros(k)
        for i in range(k):
            pts = reshaped[closest == i]
            new_centroids[i] = pts.mean() if pts.size > 0 else centroids[i]

        if np.all(np.abs(new_centroids - centroids) < tolerance):
            break

        centroids = new_centroids

    ssd = np.sum(np.min(np.abs(reshaped - centroids), axis=1) ** 2)

    return closest.reshape(x, y), centroids, ssd


# --------------------------------------------------------
# CURVATURE-BASED ELBOW DETECTION (KNEEDLE)
# --------------------------------------------------------
def find_elbow_kneedle(k_vals, ssd_vals):
    """
    Finds optimal K using curvature-based elbow method.
    """
    x = (k_vals - k_vals.min()) / (k_vals.max() - k_vals.min())
    y = (ssd_vals - ssd_vals.min()) / (ssd_vals.max() - ssd_vals.min())

    x1, y1 = x[0], y[0]
    x2, y2 = x[-1], y[-1]

    distances = np.abs(
        (y2 - y1) * x
        - (x2 - x1) * y
        + x2 * y1
        - y2 * x1
    ) / np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

    return int(k_vals[np.argmax(distances)])


# --------------------------------------------------------
# MAIN CLASSIFICATION FUNCTION
# --------------------------------------------------------
def classify_single_band_raster(file_path, max_k=10):
    """
    Classifies a single-band raster using K-means and elbow method.

    Returns:
    - labels (2D array)
    - centroids (array)
    - optimal_k (int)
    - raster profile (dict)
    """
    with rasterio.open(file_path) as src:
        if src.count != 1:
            raise ValueError("Raster must be single-band.")

        data = src.read(1).astype(float)
        profile = src.profile

    flat = data.flatten()
    ssd_vals = []
    k_vals = np.arange(1, max_k + 1)

    for k in k_vals:
        if k == 1:
            ssd = np.sum((flat - flat.mean()) ** 2)
        else:
            _, _, ssd = kmeans_single_band(data.copy(), k)
        ssd_vals.append(ssd)

    ssd_vals = np.array(ssd_vals)
    optimal_k = find_elbow_kneedle(k_vals, ssd_vals)

    labels, centroids, _ = kmeans_single_band(data, optimal_k)

    return labels, centroids, optimal_k, profile

