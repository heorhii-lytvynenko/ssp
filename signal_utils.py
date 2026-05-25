import numpy as np


def to_mono(data):
    if data.ndim == 1:
        return data.astype(float)
    return data.mean(axis=1).astype(float)


def time_axis_ms(length, samplerate, start_ms=0.0):
    return start_ms + (np.arange(length, dtype=float) / samplerate * 1000.0)
