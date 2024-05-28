import cv2
import numpy as np
import pytesseract
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


def find_dominant_color(cluster, centroids):
    labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (hist, _) = np.histogram(cluster.labels_, bins = labels)
    hist = hist.astype("float")
    hist /= hist.sum()

    colors = sorted([(percent, color) for (percent, color) in zip(hist, centroids)], key=lambda x: x[0], reverse=True)
    per, first_color = colors[0]
    return first_color.astype("uint8").tolist()

#roi = image[y-1:y+h+1, x-1:x+w+1]
def make_cluster(roi, cluster_number=5):
    roi_reshape = roi.reshape((roi.shape[0] * roi.shape[1], 3))
    cluster = KMeans(n_clusters=cluster_number, n_init=10).fit(roi_reshape)
    return cluster

def find_roi(image, x, y, w, h):
    try:
        roi = image[y-5:y+h+5, x-5:x+w+5]
    except:
        try:
            roi = image[y-1:y+h+1, x-1:x+w+1]
        except:
            roi = image[y:y+h, x:x+w]

    return roi