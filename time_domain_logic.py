import numpy as np

from constants import FRAMES_DEFAULT_MS, FRAMES_ERROR_ZERO_LEN
from quality_logic import downsample_xy
from signal_utils import time_axis_ms, to_mono


def split_signal_into_frames(data, samplerate, frame_ms=FRAMES_DEFAULT_MS, overlap_ratio=0.5):
    frame_len = int(round(samplerate * frame_ms / 1000))
    if frame_len <= 0:
        raise ValueError(FRAMES_ERROR_ZERO_LEN)
    hop_len = max(1, int(round(frame_len * (1 - overlap_ratio))))

    total_samples = len(data)
    if total_samples <= frame_len:
        starts = np.array([0], dtype=int)
        if data.ndim == 1:
            frames = np.expand_dims(np.pad(data, (0, frame_len - total_samples), mode="constant"), axis=0)
        else:
            frames = np.expand_dims(np.pad(data, ((0, frame_len - total_samples), (0, 0)), mode="constant"), axis=0)
        return frames, starts, frame_len, hop_len

    starts = np.arange(0, total_samples - frame_len + 1, hop_len, dtype=int)
    if starts[-1] != total_samples - frame_len:
        starts = np.append(starts, total_samples - frame_len)

    if data.ndim == 1:
        frames = np.stack([data[s : s + frame_len] for s in starts], axis=0)
    else:
        frames = np.stack([data[s : s + frame_len, :] for s in starts], axis=0)
    return frames, starts, frame_len, hop_len


def compute_zero_crossing_rate(frames):
    signs = np.where(frames >= 0, 1.0, -1.0)
    diffs = np.abs(signs[:, 1:] - signs[:, :-1])
    frame_len = frames.shape[1]
    return np.sum(diffs, axis=1) / (2.0 * frame_len)


def normalized_autocorrelation(signal):
    ac = np.correlate(signal, signal, mode="full")
    mid = len(ac) // 2
    ac_pos = ac[mid:]
    if ac_pos[0] != 0:
        ac_pos = ac_pos / ac_pos[0]
    lags = np.arange(len(ac_pos), dtype=int)
    return lags, ac_pos


def _select_short_analysis_segment(signal, samplerate, max_ms=30.0):
    max_len = max(1, int(round(samplerate * max_ms / 1000.0)))
    if len(signal) <= max_len:
        return signal
    start = (len(signal) - max_len) // 2
    return signal[start : start + max_len]


def estimate_f0_from_autocorr(lags, ac_pos, samplerate, fmin=50.0, fmax=500.0):
    min_lag = max(1, int(np.floor(samplerate / fmax)))
    max_lag = min(len(ac_pos) - 1, int(np.ceil(samplerate / fmin)))
    if min_lag >= max_lag:
        return None, None, None
    search = ac_pos[min_lag : max_lag + 1]
    peak_rel = int(np.argmax(search))
    peak_lag = min_lag + peak_rel
    peak_val = float(ac_pos[peak_lag])
    if peak_lag <= 0 or peak_val <= 0:
        return None, peak_lag, peak_val
    return float(samplerate / peak_lag), peak_lag, peak_val


class TimeDomainLogic:
    @staticmethod
    def build(segment, samplerate, quality, max_points):
        mono_signal = to_mono(segment)

        frames, frame_starts, frame_len, hop_len = split_signal_into_frames(mono_signal, samplerate)
        frame_energy = np.sum(frames ** 2, axis=tuple(range(1, frames.ndim)))
        frame_zcr = compute_zero_crossing_rate(frames)
        frame_times_ms = frame_starts / samplerate * 1000.0

        # For F0/autocorrelation we intentionally use a short segment (lab requirement: 15-25 ms).
        # This also keeps computation responsive even when the selected range is long.
        ac_signal = _select_short_analysis_segment(mono_signal, samplerate=samplerate, max_ms=30.0)
        ac_lags, ac_values = normalized_autocorrelation(ac_signal)
        ac_lags_ms = ac_lags / samplerate * 1000.0
        f0_hz, f0_lag, f0_peak = estimate_f0_from_autocorr(ac_lags, ac_values, samplerate)
        f0_lag_ms = (f0_lag / samplerate * 1000.0) if f0_lag is not None else None

        signal_time_full = time_axis_ms(len(mono_signal), samplerate)
        signal_time_ms, mono_signal = downsample_xy(signal_time_full, mono_signal, quality=quality, max_points=max_points)
        frame_time_full = frame_times_ms
        frame_times_ms, frame_energy = downsample_xy(frame_time_full, frame_energy, quality=quality, max_points=max_points)
        _, frame_zcr = downsample_xy(frame_time_full, frame_zcr, quality=quality, max_points=max_points)
        ac_lags_ms, ac_values = downsample_xy(ac_lags_ms, ac_values, quality=quality, max_points=max_points)

        return {
            "mode": "time_domain",
            "signal": mono_signal,
            "signal_time_ms": signal_time_ms,
            "frame_starts": frame_starts,
            "frame_times_ms": frame_times_ms,
            "frame_energy": frame_energy,
            "frame_zcr": frame_zcr,
            "autocorr_lags_ms": ac_lags_ms,
            "autocorr_values": ac_values,
            "f0_hz": f0_hz,
            "f0_lag": f0_lag,
            "f0_lag_ms": f0_lag_ms,
            "f0_peak": f0_peak,
            "frame_len": frame_len,
            "hop_len": hop_len,
        }
