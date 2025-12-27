# By : Ayman Mutasim

import numpy as np
import rasterio
import matplotlib.pyplot as plt


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

    # Compute the norms
    distances = np.abs(
        (y2 - y1) * x
        - (x2 - x1) * y
        + x2 * y1
        - y2 * x1
    ) / np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

    # Plot the SSD for different values of k
    plt.plot(k_vals, ssd_vals)
    plt.title("Elbow method: optimal k selection")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Sum of Squared Distances (SSD)")
    plt.show()
    
    return int(k_vals[np.argmax(distances)])


def save_classified_raster(classified_flat, labels, profile, optimal_k, output_filepath):
    classified_raster = classified_flat.reshape(labels.shape)
    # Explicit dtype
    classified_raster = classified_raster.astype(np.float32)
    out_profile = profile.copy()
    out_profile.update(dtype="float32", count=1)
    
    with rasterio.open(output_filepath, "w", **out_profile) as dst:
        dst.write(classified_raster, 1)
    
    print("Classified raster saved.")


# --------------------------------------------------------
# MAIN CLASSIFICATION FUNCTION
# --------------------------------------------------------
def classify_single_band_raster(input_filepath, output_filepath, max_k=10):
    """
    Classifies a single-band raster using K-means and elbow method.

    Returns:
    - labels (2D array)
    - centroids (array)
    - optimal_k (int)
    - raster profile (dict)
    """
    with rasterio.open(input_filepath) as src:
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

    classified_flat = np.zeros(labels.size, float)
    labels_flat = labels.flatten()
    
    for i in range(len(classified_flat)):
        classified_flat[i] = centroids[labels_flat[i]]

    save_classified_raster(classified_flat, labels, profile, optimal_k, output_filepath)

    return labels, centroids, optimal_k