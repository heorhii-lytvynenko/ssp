import numpy as np

from quality_logic import downsample_xy
from signal_utils import time_axis_ms, to_mono
from time_domain_logic import estimate_f0_from_autocorr, normalized_autocorrelation


def _windowed_segment(segment):
    win = np.hanning(len(segment))
    return segment * win


def _magnitude_spectrum_db(segment, samplerate):
    n = len(segment)
    fft_vals = np.fft.rfft(segment)
    mag = np.abs(fft_vals)
    mag_db = 20.0 * np.log10(np.maximum(mag, 1e-12))
    freq_khz = np.fft.rfftfreq(n, d=1.0 / samplerate) / 1000.0
    return freq_khz, mag_db


def _real_cepstrum(segment, samplerate):
    spectrum = np.fft.rfft(segment)
    log_mag = np.log(np.maximum(np.abs(spectrum), 1e-12))
    # Keep cepstrum length equal to the original segment length.
    cep = np.fft.irfft(log_mag, n=len(segment))
    quef_ms = np.arange(len(cep), dtype=float) / samplerate * 1000.0
    return quef_ms, cep


def _estimate_f0_from_cepstrum(cep, samplerate, fmin=70.0, fmax=500.0):
    qmin = int(np.floor(samplerate / fmax))
    qmax = int(np.ceil(samplerate / fmin))
    qmax = min(qmax, len(cep) - 1)
    if qmin >= qmax:
        return None, None, None
    search = cep[qmin : qmax + 1]
    # Avoid trivial boundary selections by preferring interior local maxima.
    if len(search) >= 3:
        mids = np.where((search[1:-1] > search[:-2]) & (search[1:-1] >= search[2:]))[0] + 1
        if len(mids) > 0:
            best_mid = mids[int(np.argmax(search[mids]))]
            peak_idx = qmin + int(best_mid)
        else:
            peak_idx = qmin + int(np.argmax(search))
    else:
        peak_idx = qmin + int(np.argmax(search))
    peak_val = float(cep[peak_idx])
    if peak_idx <= 0:
        return None, peak_idx, peak_val
    return float(samplerate / peak_idx), peak_idx, peak_val


def _spectrogram(signal, samplerate, frame_ms=20.0, overlap_ratio=0.5):
    frame_len = max(1, int(round(samplerate * frame_ms / 1000.0)))
    hop = max(1, int(round(frame_len * (1.0 - overlap_ratio))))
    if len(signal) < frame_len:
        signal = np.pad(signal, (0, frame_len - len(signal)))
    starts = np.arange(0, len(signal) - frame_len + 1, hop, dtype=int)
    if len(starts) == 0:
        starts = np.array([0], dtype=int)
    win = np.hanning(frame_len)
    spec = []
    for s in starts:
        frame = signal[s : s + frame_len] * win
        mag = np.abs(np.fft.rfft(frame))
        spec.append(20.0 * np.log10(np.maximum(mag, 1e-12)))
    spec = np.array(spec).T
    times_ms = starts / samplerate * 1000.0
    freqs_khz = np.fft.rfftfreq(frame_len, d=1.0 / samplerate) / 1000.0
    return times_ms, freqs_khz, spec


class FrequencyDomainLogic:
    _spectrogram_cache = {}

    @staticmethod
    def build(segment, full_signal, samplerate, quality, max_points):
        mono_seg = to_mono(segment)
        mono_full = to_mono(full_signal)
        if len(mono_seg) < 4:
            return {
                "mode": "frequency_domain",
                "error": "Segment too short for frequency analysis.",
            }
        seg_time_ms = time_axis_ms(len(mono_seg), samplerate)

        win_seg = _windowed_segment(mono_seg)
        spec_freq_khz, spec_db = _magnitude_spectrum_db(win_seg, samplerate)
        quef_ms, cep = _real_cepstrum(win_seg, samplerate)
        f0_cep_hz, f0_cep_idx, f0_cep_peak = _estimate_f0_from_cepstrum(cep, samplerate)
        f0_cep_ms = (f0_cep_idx / samplerate * 1000.0) if f0_cep_idx is not None else None

        ac_lags, ac_vals = normalized_autocorrelation(mono_seg)
        f0_ac_hz, f0_ac_lag, _ = estimate_f0_from_autocorr(ac_lags, ac_vals, samplerate)
        f0_ac_ms = (f0_ac_lag / samplerate * 1000.0) if f0_ac_lag is not None else None

        spectrogram_error = None
        try:
            cache_key = (len(mono_full), float(np.mean(mono_full[: min(len(mono_full), 200)])), samplerate)
            if cache_key in FrequencyDomainLogic._spectrogram_cache:
                sp_t_ms, sp_f_khz, sp_db = FrequencyDomainLogic._spectrogram_cache[cache_key]
            else:
                sp_t_ms, sp_f_khz, sp_db = _spectrogram(mono_full, samplerate)
                FrequencyDomainLogic._spectrogram_cache[cache_key] = (sp_t_ms, sp_f_khz, sp_db)
        except Exception as exc:
            sp_t_ms = np.array([], dtype=float)
            sp_f_khz = np.array([], dtype=float)
            sp_db = np.zeros((1, 1), dtype=float)
            spectrogram_error = str(exc)

        seg_time_ms, mono_seg_plot = downsample_xy(seg_time_ms, mono_seg, quality=quality, max_points=max_points)
        spec_freq_khz, spec_db = downsample_xy(spec_freq_khz, spec_db, quality=quality, max_points=max_points)
        quef_ms, cep = downsample_xy(quef_ms, cep, quality=quality, max_points=max_points)

        return {
            "mode": "frequency_domain",
            "segment_time_ms": seg_time_ms,
            "segment_signal": mono_seg_plot,
            "spectrum_freq_khz": spec_freq_khz,
            "spectrum_db": spec_db,
            "cepstrum_quef_ms": quef_ms,
            "cepstrum_values": cep,
            "f0_cep_hz": f0_cep_hz,
            "f0_cep_ms": f0_cep_ms,
            "f0_cep_peak": f0_cep_peak,
            "f0_ac_hz": f0_ac_hz,
            "f0_ac_ms": f0_ac_ms,
            "spectrogram_time_ms": sp_t_ms,
            "spectrogram_freq_khz": sp_f_khz,
            "spectrogram_db": sp_db,
            "spectrogram_error": spectrogram_error,
        }
