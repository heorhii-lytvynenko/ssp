import numpy as np


def compute_sample_indices(length, quality="Medium", max_points=4000):
    if quality == "High" or length <= max_points:
        return np.arange(length, dtype=int)
    return np.linspace(0, length - 1, max_points, dtype=int)


def downsample_by_indices(vector, indices):
    return vector[indices]


def downsample_vector(vector, quality="Medium", max_points=4000):
    idx = compute_sample_indices(len(vector), quality=quality, max_points=max_points)
    return downsample_by_indices(vector, idx)


def downsample_xy(x, y, quality="Medium", max_points=4000):
    idx = compute_sample_indices(len(x), quality=quality, max_points=max_points)
    return downsample_by_indices(x, idx), downsample_by_indices(y, idx)


def downsample_time_and_segment(time, segment, quality="Medium", max_points=4000):
    idx = compute_sample_indices(len(time), quality=quality, max_points=max_points)
    if segment.ndim == 1:
        return downsample_by_indices(time, idx), downsample_by_indices(segment, idx)
    return downsample_by_indices(time, idx), segment[idx, :]
