import numpy as np

from signal_utils import time_axis_ms, to_mono


def _frame_signal(signal, frame_len):
    n_frames = int(np.ceil(len(signal) / frame_len))
    pad = n_frames * frame_len - len(signal)
    padded = np.pad(signal, (0, pad), mode="constant")
    return padded.reshape(n_frames, frame_len), len(signal)


def _snr_db_from_powers(p_sig, p_noise):
    p_sig = float(p_sig) + 1e-12
    p_noise = float(p_noise) + 1e-12
    return 10.0 * np.log10(p_sig / p_noise)


class EnhancementLogic:
    @staticmethod
    def build(full_signal, samplerate, noise_start_sample, noise_end_sample):
        x = to_mono(full_signal)
        nseg = x[noise_start_sample:noise_end_sample]
        if len(nseg) < 4:
            nseg = x[: min(len(x), int(0.02 * samplerate))]

        frame_len = max(1, int(round(0.02 * samplerate)))
        win = np.hanning(frame_len)

        noise_frames, _ = _frame_signal(nseg, frame_len)
        noise_mag = []
        for fr in noise_frames:
            noise_mag.append(np.abs(np.fft.rfft(fr * win)))
        noise_mag = np.mean(np.array(noise_mag), axis=0)

        frames, orig_len = _frame_signal(x, frame_len)
        out = []
        floor_ratio = 0.05
        for fr in frames:
            spec = np.fft.rfft(fr * win)
            mag = np.abs(spec)
            phase = np.angle(spec)
            clean_mag = np.maximum(mag - noise_mag, floor_ratio * noise_mag)
            clean_spec = clean_mag * np.exp(1j * phase)
            clean_fr = np.fft.irfft(clean_spec, n=frame_len)
            out.append(clean_fr)
        enhanced = np.concatenate(out)[:orig_len]

        n0 = max(0, noise_start_sample)
        n1 = min(len(x), noise_end_sample)
        noise_before = x[n0:n1] if n1 > n0 else x[: min(len(x), frame_len)]
        noise_after = enhanced[n0:n1] if n1 > n0 else enhanced[: min(len(x), frame_len)]
        if n1 > n0 and (n0 > 0 or n1 < len(x)):
            sig_region_before = np.concatenate((x[:n0], x[n1:]))
            sig_region_after = np.concatenate((enhanced[:n0], enhanced[n1:]))
        else:
            sig_region_before = x
            sig_region_after = enhanced

        p_sig_before = np.mean(sig_region_before ** 2)
        p_noise_before = np.mean(noise_before ** 2)
        p_sig_after = np.mean(sig_region_after ** 2)
        p_noise_after = np.mean(noise_after ** 2)
        snr_before = _snr_db_from_powers(p_sig_before, p_noise_before)
        snr_after = _snr_db_from_powers(p_sig_after, p_noise_after)

        t_ms = time_axis_ms(len(x), samplerate)
        return {
            "mode": "enhancement",
            "time_ms": t_ms,
            "noisy_signal": x,
            "enhanced_signal": enhanced,
            "snr_before_db": float(snr_before),
            "snr_after_db": float(snr_after),
            "frame_ms": 20.0,
        }
