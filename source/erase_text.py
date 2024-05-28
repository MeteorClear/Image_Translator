import numpy as np
from sklearn.cluster import KMeans

'''
Estimating the color of a particular area from the image
K-means clustering method using sklearn is used for color estimation
Used to estimate background color and character color
'''

def find_roi(image: np.ndarray, \
             x: int, \
             y: int, \
             w: int, \
             h: int) -> np.ndarray:
    '''
    Sliced image array by coordinate
    '''
    image_height, image_width, _c = image.shape

    # Generally, uses a range larger than the letter area
    # Cause if the letter is thick, the color area is wider than the background,
    # So the background color and character color can change the estimation result
    # Adjusted to maximum/minimum value when position value exceeds image area
    try:
        roi = image[max(0, y-5) : min(image_height, y+h+5), \
                    max(0, x-5) : min(image_width, x+w+5)]
        
    except:
        # Structurally rarely used
        try:
            roi = image[max(0, y-1) : min(image_height, y+h+1), \
                        max(0, x-1) : min(image_width, x+w+1)]
        except:
            roi = image[y:y+h, x:x+w]
    
    # Also structurally rarely used
    if len(roi) < 1:
        roi = image[y:y+h, x:x+w]

    return roi


def make_cluster(roi: np.ndarray, \
                 cluster_number:int=5) -> KMeans:
    '''
    Create a cluster, 
    Using K-Means clustering
    '''
    # shape[0] and shape[1] is height and width
    roi_reshape = roi.reshape((roi.shape[0] * roi.shape[1], 3))

    # The higher n_clusters, more accurate results can be estimated, but longer run time
    # Values of 4 to 8 seem reasonable
    cluster = KMeans(n_clusters=cluster_number, n_init=10).fit(roi_reshape)

    return cluster


def find_dominant_color(cluster: KMeans, \
                        centroids: np.ndarray= None, \
                        order:int=0) -> list:
    '''
    Sort clusters in color clusters
    '''
    if centroids is None:
        centroids = cluster.cluster_centers_

    # Create Labeled Array
    labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)

    # Create and normalize histograms
    (hist, _) = np.histogram(cluster.labels_, bins = labels)
    hist = hist.astype("float")
    hist /= hist.sum()

    # Sorts normalized histograms in descending order for percentages
    colors = sorted([(percent, color) for (percent, color) in zip(hist, centroids)], \
                    key=lambda x: x[0], \
                    reverse=True)
    
    # In general, for the character area, the background occupies a larger area than the letter, 
    # So the color with the highest proportion is estimated to be the background color
    # Also, the color of the second proportion is assumed to be the color of the letter 
    # Because the color of the letter will occupy the second largest area after the color of the background
    # This method can cause a reversal of background color and font color on thick font, 
    # But it generally appears to be the most suitable method, It even operates normally
    per, first_color = colors[order]

    return first_color.astype("uint8").tolist()


def correction_color(color: tuple, \
                     value: int, \
                     mode=False) -> tuple:
    '''
    Return color by adding or subtracting value
    '''
    # In the case of handwriting color, it shows a phenomenon of being biased toward the background color during the clustering process
    # To correct this by adding or subtracting a specific value to the color of the text
    # I don't know if this works, but it's better than nothing at the moment
    if mode:
        modify_color = tuple(map(lambda x : min(x+value, 255), list(color)))
    else:
        modify_color = tuple(map(lambda x : max(x-value, 0), list(color)))

    return modify_color