import rasterio
import numpy as np


def load_raster(path):
    """Load a single-band raster and return it as a normalized float array."""
    with rasterio.open(path) as src:
        data = src.read(1).astype(float)
    # Normalize to [0, 1] range (skip if it's the initial fire grid with values 0/1/2)
    return data


def normalize(arr):
    """Normalize array values to [0, 1]."""
    min_val, max_val = arr.min(), arr.max()
    if max_val == min_val:
        return np.zeros_like(arr)
    return (arr - min_val) / (max_val - min_val)
