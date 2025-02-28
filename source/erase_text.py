import numpy as np
from sklearn.cluster import KMeans

"""
Estimate colors in a specific region of an image using K-means clustering.
This is used to determine the background and character colors.
"""

def find_roi(image: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    """
    Extract a region of interest (ROI) from the image based on coordinates.

    The ROI is slightly expanded beyond the specified boundaries to accommodate cases 
    where thick characters might affect the estimation of background and text colors.

    Args:
        image (np.ndarray): The input image array.
        x (int): X-coordinate of the top-left corner of the ROI.
        y (int): Y-coordinate of the top-left corner of the ROI.
        w (int): Width of the ROI.
        h (int): Height of the ROI.

    Returns:
        np.ndarray: The extracted ROI.
    """
    image_height, image_width, _ = image.shape

    for margin in [5, 1, 0]:
        try:
            roi = image[ \
                max(0, y - margin) : min(image_height, y + h + margin), \
                max(0, x - margin) : min(image_width, x + w + margin) \
            ]

            if roi.size > 0:
                return roi
        except:
            continue

    return image[y:y+h, x:x+w]


def make_cluster(roi: np.ndarray, cluster_number: int = 5) -> KMeans:
    """
    Perform K-means clustering on the ROI to group similar colors.

    The ROI is reshaped into a 2D array where each row represents a pixel's RGB values.
    A higher number of clusters may yield more accurate color estimates at the cost of increased runtime.

    Args:
        roi (np.ndarray): The region of interest.
        cluster_number (int, optional): The number of clusters for K-means. Defaults to 5.

    Returns:
        KMeans: The fitted sklearn KMeans clustering model.
    """
    # Reshape the ROI to a 2D array (each pixel is a row with 3 color channels).
    roi_reshape = roi.reshape((roi.shape[0] * roi.shape[1], 3))
    cluster = KMeans(n_clusters=cluster_number, n_init=10).fit(roi_reshape)

    return cluster


def find_dominant_color(cluster: KMeans, \
                        centroids: np.ndarray = None, \
                        order: int = 0) -> list:
    """
    Identify the dominant color from the clustered ROI.

    Clusters are sorted by the percentage of pixels they contain.
    Typically, the most prevalent color (order 0) is assumed to be the background,
    while the second most prevalent (order 1) might represent the text color.

    Note that in some cases, such as with thick fonts, these roles may be reversed.

    Args:
        cluster (KMeans): The fitted KMeans clustering model.
        centroids (np.ndarray, optional): Array of cluster centers. Defaults to the model's centers.
        order (int, optional): The order of the color to return (0 for the most dominant). Defaults to 0.

    Returns:
        list: The dominant color as an RGB list with values in the range [0, 255].
    """
    if centroids is None:
        centroids = cluster.cluster_centers_

    # Create a histogram of cluster labels.
    bins = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (hist, _) = np.histogram(cluster.labels_, bins = bins)
    hist = hist.astype("float")
    hist /= hist.sum()

    # Pair each centroid with its normalized percentage and sort in descending order.
    colors = sorted([(percent, color) for (percent, color) in zip(hist, centroids)], \
                    key=lambda x: x[0], \
                    reverse=True)
    
    # Select the color based on the specified order.
    per, first_color = colors[order]

    return first_color.astype("uint8").tolist()


def correction_color(color: tuple, \
                     value: int, \
                     mode=False) -> tuple:
    """
    Adjust the brightness of a given color.

    This function modifies the color by either increasing or decreasing its brightness.
    When mode is True, the color is brightened; when False, it is darkened.
    The adjusted values are clamped between 0 and 255.

    Args:
        color (tuple): The original RGB color.
        value (int): The adjustment value to add or subtract.
        mode (bool, optional): True to brighten, False to darken. Defaults to False.

    Returns:
        tuple: The adjusted RGB color.
    """
    if mode:
        # Increase brightness, ensuring the value does not exceed 255.
        modified_color = tuple(min(c + value, 255) for c in color)
    else:
        # Decrease brightness, ensuring the value does not go below 0.
        modified_color = tuple(max(c - value, 0) for c in color)

    return modified_color